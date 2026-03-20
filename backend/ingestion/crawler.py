import asyncio
import aiohttp
import uuid

from database.chroma_client import ChromaClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer

# =========================
# CONFIG
# =========================
BASE_URLS = [
    "https://handbook.gitlab.com/",
    "https://about.gitlab.com/direction/"
]

MAX_CONCURRENT_TASKS = 10
CRAWLER_WORKERS = 5
MAX_EMBED_WORKERS = 8
BATCH_SIZE = 32

EXCLUDE_PATTERNS = [
    "login", "sign_in", "register",
    "forum", "support", "customers",
    "auth", "/-/", "trial",
    "/de-", "/fr-", "/es-", "/ja-", "/pt-"
]

# =========================
# INIT
# =========================
executor = ThreadPoolExecutor(max_workers=MAX_EMBED_WORKERS)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

task_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

# =========================
# HELPERS
# =========================
def is_allowed_path(url):
    return any(url.startswith(base) for base in BASE_URLS)

def is_valid_url(url):
    return not any(p in url for p in EXCLUDE_PATTERNS)

def clean_html(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()
    return soup

# =========================
# CHUNKING
# =========================
def semantic_chunk(html):
    soup = clean_html(html)

    text = soup.get_text(" ", strip=True)

    if len(text) > 200000:
        print("⚠️ Skipping huge page")
        return []

    chunks = []
    current = ""

    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        txt = tag.get_text(" ", strip=True)

        if not txt:
            continue

        if tag.name in ["h1", "h2", "h3"]:
            if current.strip():
                chunks.append(current.strip())
                current = ""
            current += txt + ". "
        else:
            current += txt + " "

    if current.strip():
        chunks.append(current.strip())

    if len(chunks) > 200:
        print(f"⚠️ Too many chunks ({len(chunks)}), skipping")
        return []

    return chunks


def split_chunks(chunks, max_words=400, overlap=80):
    final = []

    for chunk in chunks:
        words = chunk.split()

        if len(words) <= max_words:
            final.append(chunk)
        else:
            start = 0
            while start < len(words):
                part = " ".join(words[start:start+max_words])
                final.append(part)
                start += max_words - overlap

    return final


def build_metadata(url):
    parts = [p for p in url.strip("/").split("/") if p]
    title = parts[-1] if parts else "home"

    return {
        "url": url,
        "title": title.replace("-", " ").title(),
        "topic": "General"
    }

# =========================
# EMBEDDING
# =========================
def embed_texts(texts):
    return embedder.encode(texts).tolist()

# =========================
# CRAWLER
# =========================
class Crawler:

    def __init__(self):
        self.queue = asyncio.Queue()
        self.visited = set()
        self.seen = set()

        self.buffer = []
        self.buffer_lock = asyncio.Lock()
        self.flush_lock = asyncio.Lock()

        self.chroma_client = ChromaClient()

    async def fetch(self, session, url):
        for attempt in range(3):
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as r:
                    if r.status == 200:
                        return await r.text()
            except Exception:
                print(f"❌ Retry {attempt+1}: {url}")

            await asyncio.sleep(1)

        return None

    async def store_chunks(self, chunks, url):

        metadata = build_metadata(url)

        async with self.buffer_lock:
            for chunk in chunks:
                if len(chunk.strip()) < 30:  # skip junk
                    continue

                self.buffer.append({
                    "text": chunk,
                    "metadata": metadata
                })

            if len(self.buffer) >= BATCH_SIZE:
                await self.flush_buffer()

    async def flush_buffer(self):

        async with self.flush_lock:
            if not self.buffer:
                return

            texts = [x["text"] for x in self.buffer]
            metas = [x["metadata"] for x in self.buffer]

            loop = asyncio.get_running_loop()

            embeddings = await loop.run_in_executor(
                executor,
                embed_texts,
                texts
            )

            ids = [str(uuid.uuid4()) for _ in texts]

            self.chroma_client.add_documents(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metas
            )

            print(f"🚀 Stored {len(texts)} chunks")

            self.buffer = []

    async def process(self, session, url):

        async with task_semaphore:

            print(f"🔄 Crawling: {url}")

            html = await self.fetch(session, url)
            if not html:
                return

            chunks = semantic_chunk(html)
            chunks = split_chunks(chunks)

            if not chunks:
                return

            print(f"📦 {len(chunks)} chunks extracted")

            await self.store_chunks(chunks, url)

            soup = BeautifulSoup(html, "lxml")

            for tag in soup.find_all("a", href=True):
                link = urljoin(url, tag["href"])
                clean = link.split("#")[0].split("?")[0].rstrip("/")

                if not is_allowed_path(clean):
                    continue

                if not is_valid_url(clean):
                    continue

                if clean not in self.seen:
                    self.seen.add(clean)
                    await self.queue.put(clean)

    async def worker(self, session):

        while True:
            url = await self.queue.get()

            if url is None:
                self.queue.task_done()
                break

            if url in self.visited:
                self.queue.task_done()
                continue

            self.visited.add(url)

            await self.process(session, url)

            self.queue.task_done()

    async def run(self):

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        async with aiohttp.ClientSession(headers=headers) as session:

            for url in BASE_URLS:
                self.seen.add(url)
                await self.queue.put(url)

            workers = [
                asyncio.create_task(self.worker(session))
                for _ in range(CRAWLER_WORKERS)
            ]

            await self.queue.join()

            print("✅ Crawling finished")

            await self.flush_buffer()

            for _ in workers:
                await self.queue.put(None)

            await asyncio.gather(*workers)


# =========================
# MAIN
# =========================
async def main():
    crawler = Crawler()
    await crawler.run()


if __name__ == "__main__":
    asyncio.run(main())