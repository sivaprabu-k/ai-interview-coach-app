from app.models.document import Document
from app.models import User
from app.core.security import hash_password
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document.document_retrieval_service import (
    DocumentRetrievalService,
)
from types import SimpleNamespace
from app.services.document.document_answer_service import DocumentAnswerService


def test_list_documents(client, db_session, auth_user, auth_headers):
    document = Document(
        user_id=auth_user.id,
        filename="blog.pdf",
        file_path="uploads/blog.pdf",
        content_type="application/pdf",
        file_size=1024,
        status="processed",
    )

    db_session.add(document)
    db_session.flush()

    response = client.get(
        "/api/v1/documents/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status"] is True
    assert len(response_data["data"]) == 1
    assert response_data["data"][0]["filename"] == "blog.pdf"


def test_list_documents_user_isolation(
    client,
    db_session,
    auth_user,
    auth_headers,
):
    another_user = User(
        name="Another Test User",
        email="another-test@example.com",
        hashed_password=hash_password("TestPass123!"),
        is_active=True,
    )

    db_session.add(another_user)
    db_session.flush()

    own_document = Document(
        user_id=auth_user.id,
        filename="my_document.pdf",
        file_path="uploads/my_document.pdf",
        content_type="application/pdf",
        file_size=1024,
        status="processed",
    )

    other_document = Document(
        user_id=another_user.id,
        filename="other_document.pdf",
        file_path="uploads/other_document.pdf",
        content_type="application/pdf",
        file_size=2048,
        status="processed",
    )

    db_session.add_all([own_document, other_document])
    db_session.flush()

    response = client.get(
        "/api/v1/documents/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    filenames = [
        item["filename"]
        for item in response.json()["data"]
    ]

    assert "my_document.pdf" in filenames
    assert "other_document.pdf" not in filenames


def test_upload_document_success(
    client,
    db_session,
    auth_user,
    auth_headers,
    monkeypatch,
    tmp_path,
):
    from app.api.v1 import endpoints

    import app.api.v1.endpoints.documents as documents_module

    monkeypatch.setattr(
        documents_module,
        "UPLOAD_DIR",
        tmp_path,
    )

    class MockIngestionService:
        def ingest_document(self, db, document):
            document.status = "processed"
            db.commit()
            db.refresh(document)
            return document

    monkeypatch.setattr(
        documents_module,
        "DocumentIngestionService",
        MockIngestionService,
    )

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={
            "file": (
                "sample.pdf",
                b"%PDF-1.4 test content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["status"] is True
    assert response_data["data"]["filename"] == "sample.pdf"
    assert response_data["data"]["status"] == "processed"

    document = (
        db_session.query(Document)
        .filter(Document.filename == "sample.pdf")
        .first()
    )

    assert document is not None
    assert document.user_id == auth_user.id
    assert document.status == "processed"


def test_upload_document_invalid_extension(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={
            "file": (
                "sample.exe",
                b"invalid file content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400

    response_data = response.json()

    assert response_data["status"] is False
    assert "Only PDF and DOCX" in response_data["message"]


def test_retrieve_relevant_chunks(db_session, auth_user, monkeypatch):
    embedding = [0.01] * 768

    class MockEmbeddingService:
        def generate_embedding(self, text):
            return embedding

    monkeypatch.setattr(
        "app.services.document.document_retrieval_service.EmbeddingService",
        MockEmbeddingService,
    )

    document = Document(
        user_id=auth_user.id,
        filename="blog.pdf",
        file_path="uploads/blog.pdf",
        content_type="application/pdf",
        file_size=1000,
        status="processed",
    )
    db_session.add(document)
    db_session.flush()

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="The blog application uses React, Django, and PostgreSQL.",
        embedding=embedding,
    )
    db_session.add(chunk)
    db_session.flush()

    service = DocumentRetrievalService()

    results = service.retrieve_relevant_chunks(
        db=db_session,
        query="Which technologies are used?",
        user_id=auth_user.id,
    )

    assert len(results) == 1
    assert results[0][0].content == (
        "The blog application uses React, Django, and PostgreSQL."
    )
    assert results[0][1] <= 0.35


def test_retrieve_chunks_user_isolation(
    db_session,
    auth_user,
    monkeypatch,
):
    embedding = [0.01] * 768

    class MockEmbeddingService:
        def generate_embedding(self, text):
            return embedding

    monkeypatch.setattr(
        "app.services.document.document_retrieval_service.EmbeddingService",
        MockEmbeddingService,
    )

    another_user = User(
        name="Another User",
        email="another-user@example.com",
        hashed_password=hash_password("TestPass123!"),
        is_active=True,
    )
    db_session.add(another_user)
    db_session.flush()

    own_document = Document(
        user_id=auth_user.id,
        filename="own.pdf",
        file_path="uploads/own.pdf",
        content_type="application/pdf",
        file_size=1000,
        status="processed",
    )

    another_document = Document(
        user_id=another_user.id,
        filename="another.pdf",
        file_path="uploads/another.pdf",
        content_type="application/pdf",
        file_size=1000,
        status="processed",
    )

    db_session.add_all([own_document, another_document])
    db_session.flush()

    db_session.add_all([
        DocumentChunk(
            document_id=own_document.id,
            chunk_index=0,
            content="My document content.",
            embedding=embedding,
        ),
        DocumentChunk(
            document_id=another_document.id,
            chunk_index=0,
            content="Another user's document content.",
            embedding=embedding,
        ),
    ])
    db_session.flush()

    service = DocumentRetrievalService()

    results = service.retrieve_relevant_chunks(
        db=db_session,
        query="Find document content",
        user_id=auth_user.id,
    )

    assert len(results) == 1
    assert results[0][0].content == "My document content."


def test_generate_document_answer(db_session, monkeypatch):
    class MockRetrievalService:
        def retrieve_relevant_chunks(self, **kwargs):
            chunk = SimpleNamespace(
                content="The blog application uses React, Django, and PostgreSQL."
            )
            return [(chunk, 0.1)]

    class MockGeminiClient:
        class Models:
            def generate_content(self, **kwargs):
                return SimpleNamespace(
                    text="The application uses React, Django, and PostgreSQL."
                )

        models = Models()

    monkeypatch.setattr(
        "app.services.document.document_answer_service.settings.gemini_api_key",
        "test-api-key",
    )
    monkeypatch.setattr(
        "app.services.document.document_answer_service.genai.Client",
        lambda **kwargs: MockGeminiClient(),
    )
    monkeypatch.setattr(
        "app.services.document.document_answer_service.DocumentRetrievalService",
        MockRetrievalService,
    )

    service = DocumentAnswerService()

    answer = service.generate_answer(
        db=db_session,
        query="Which technologies are used?",
        user_id=1,
    )

    assert answer == (
        "The application uses React, Django, and PostgreSQL."
    )

def test_generate_document_answer_without_context(
    db_session,
    monkeypatch,
):
    class MockRetrievalService:
        def retrieve_relevant_chunks(self, **kwargs):
            return []

    monkeypatch.setattr(
        "app.services.document.document_answer_service.settings.gemini_api_key",
        "test-api-key",
    )
    monkeypatch.setattr(
        "app.services.document.document_answer_service.DocumentRetrievalService",
        MockRetrievalService,
    )

    service = DocumentAnswerService()

    answer = service.generate_answer(
        db=db_session,
        query="What is the application about?",
        user_id=1,
    )

    assert answer == (
        "I don't have relevant information in the uploaded "
        "documents to answer this question."
    )

def test_ask_document_question_success(
    client,
    auth_headers,
    auth_user,
    monkeypatch,
):
    class MockDocumentAnswerService:
        def generate_answer(self, db, query, user_id, top_k):
            assert query == "Which technologies are used?"
            assert user_id == auth_user.id
            assert top_k == 5

            return "React, Django, and PostgreSQL."

    monkeypatch.setattr(
        "app.api.v1.endpoints.documents.DocumentAnswerService",
        MockDocumentAnswerService,
    )

    response = client.post(
        "/api/v1/documents/ask",
        json={
            "query": "Which technologies are used?",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status"] is True
    assert response_data["data"]["question"] == (
        "Which technologies are used?"
    )
    assert response_data["data"]["answer"] == (
        "React, Django, and PostgreSQL."
    )

def test_ask_document_question_unauthorized(client):
    response = client.post(
        "/api/v1/documents/ask",
        json={
            "query": "Which technologies are used?",
        },
    )

    assert response.status_code == 401

def test_ask_document_question_empty_query(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/documents/ask",
        json={
            "query": "",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_ask_document_question_invalid_top_k(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/documents/ask",
        json={
            "query": "Explain the application.",
            "top_k": 15,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
