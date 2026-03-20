from fastapi import APIRouter, Request, HTTPException, Body, Header


def get_router(rag_service):
    """
    Create API router with injected RAG service.
    """

    router = APIRouter()

    @router.get("/health")
    async def health_check():
        """
        Health check endpoint.
        """
        return {"status": "ok"}

    # @router.post("/chat")
    # async def chat(request: Request):
    #     """
    #     Chat endpoint for the GitLab GenAI chatbot.
    #     """

    #     try:
    #         body = await request.json()
    #     except Exception:
    #         raise HTTPException(status_code=400, detail="Invalid JSON request")

    #     question = body.get("question")
    #     topic = body.get("topic")

    #     if not question:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Missing required field: 'question'"
    #         )

    #     try:
    #         response = rag_service.handle_query(
    #             question=question,
    #             topic=topic
    #         )
    #         return response

    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=500,
    #             detail=f"Query processing failed: {str(e)}"
    #         )



    # @router.post("/chat")
    # async def chat(question: str = Body(..., media_type="text/plain")):
    #     """
    #     Chat endpoint that accepts raw text body.
    #     """

    #     if not question.strip():
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Empty question provided"
    #         )

    #     try:
    #         response = rag_service.handle_query(
    #             question=question,
    #             topic=None
    #         )
    #         return response

    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=500,
    #             detail=f"Query processing failed: {str(e)}"
    #         )


    @router.post("/chat")
    async def chat(
        session_id: str = Header(...),
        question: str = Body(..., media_type="text/plain")
    ):
        """
        Chat endpoint:
        - session_id → from headers
        - question → from raw text body
        """

        # ✅ Validate session_id
        if not session_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Empty session_id in headers"
            )

        # ✅ Validate question
        if not question or not question.strip():
            raise HTTPException(
                status_code=400,
                detail="Empty question provided"
            )

        try:
            response = rag_service.handle_query(
                question=question,
                session_id=session_id,
                topic=None
            )
            return response

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Query processing failed: {str(e)}"
            )
    
    
    
    return router