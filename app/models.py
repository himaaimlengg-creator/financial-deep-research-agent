from typing import Optional
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    text: str
    page: int


class ResearchTask(BaseModel):
    id: str
    question: str
    purpose: str
    priority: int = 1


class ResearchPlan(BaseModel):
    original_question: str
    tasks: list[ResearchTask]


class Source(BaseModel):
    title: str
    source_type: str
    url: Optional[str] = None
    page: Optional[str] = None


class Evidence(BaseModel):
    claim: str
    evidence: str
    source: Source
    confidence: float = Field(default=0.5, ge=0, le=1)


class TaskResult(BaseModel):
    task_id: str
    question: str
    findings: list[Evidence] = Field(default_factory=list)


class MissingResearch(BaseModel):
    area: str
    reason: str
    research_question: Optional[str] = None


class VerificationResult(BaseModel):
    passed: bool

    unsupported_claims: list[str] = Field(
        default_factory=list
    )

    conflicts: list[str] = Field(
        default_factory=list
    )

    missing_research: list[MissingResearch] = Field(
        default_factory=list
    )

    notes: list[str] = Field(
        default_factory=list
    )


class FinalReport(BaseModel):
    title: str
    question: str
    executive_summary: str

    key_findings: list[str] = Field(
        default_factory=list
    )

    detailed_analysis: str

    conflicting_evidence: list[str] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )

    final_synthesis: str

    sources: list[Source] = Field(
        default_factory=list
    )


