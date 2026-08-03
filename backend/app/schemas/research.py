from pydantic import BaseModel


class ResearchRequest(BaseModel):
    topic: str


class SourceOut(BaseModel):
    id: int
    title: str
    url: str


class FindingOut(BaseModel):
    id: int
    content: str
    classification: str
    confidence: float
    source: SourceOut


class ContradictionOut(BaseModel):
    finding_a_id: int
    finding_b_id: int
    explanation: str


class ConclusionOut(BaseModel):
    summary: str
    supporting_finding_ids: list[int]


class QuestionOut(BaseModel):
    id: int
    text: str
    findings: list[FindingOut]
    contradictions: list[ContradictionOut]
    conclusion: ConclusionOut


class ResearchResponse(BaseModel):
    project_id: int
    topic: str
    status: str
    questions: list[QuestionOut]
    total_sources: int
    final_report: str
