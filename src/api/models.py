from pydantic import BaseModel


class EngineResult(BaseModel):
    engine: str
    label: str
    text: str
    seconds: float
    chars: int
    uses_network: bool
    noise: float
    cer: float | None = None
    wer: float | None = None
    error: str | None = None


class ProcessResponse(BaseModel):
    filename: str
    has_reference: bool
    reference: str | None = None
    results: list[EngineResult]
    timestamp: str


class HistoryEntry(BaseModel):
    filename: str
    timestamp: str
    results: list[EngineResult]
