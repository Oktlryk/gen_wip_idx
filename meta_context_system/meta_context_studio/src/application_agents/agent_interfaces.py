from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ApplicationRequirements(BaseModel):
    """Defines the high-level requirements for an application to be generated."""
    name: str = Field(..., description="Name of the application.")
    description: str = Field(..., description="A detailed description of the application's purpose and functionality.")
    key_features: List[str] = Field(default_factory=list, description="List of key features the application should have.")
    target_users: str = Field(..., description="Description of the primary users of the application.")
    technologies_preferred: List[str] = Field(default_factory=list, description="Preferred technologies or frameworks (optional).")
    technologies_avoid: List[str] = Field(default_factory=list, description="Technologies to avoid (optional).")

class ArchitecturalPlan(BaseModel):
    """Represents the architectural plan for an application."""
    application_name: str = Field(..., description="Name of the application.")
    overview: str = Field(..., description="High-level overview of the architecture.")
    components: List[Dict[str, Any]] = Field(default_factory=list, description="List of architectural components (e.g., frontend, backend, database).")
    data_models: List[Dict[str, Any]] = Field(default_factory=list, description="Key data models and their relationships.")
    api_endpoints: List[Dict[str, Any]] = Field(default_factory=list, description="Description of key API endpoints.")
    security_considerations: str = Field("", description="Security considerations and recommendations.")
    scalability_considerations: str = Field("", description="Scalability considerations and recommendations.")

class BackendCode(BaseModel):
    """Represents generated backend code."""
    file_path: str = Field(..., description="Relative path to the backend code file.")
    content: str = Field(..., description="Content of the backend code file.")
    language: str = Field("Python", description="Programming language of the backend code.")
    framework: Optional[str] = Field(None, description="Backend framework used.")

class FrontendCode(BaseModel):
    """Represents generated frontend code."""
    file_path: str = Field(..., description="Relative path to the frontend code file.")
    content: str = Field(..., description="Content of the frontend code file.")
    language: str = Field("JavaScript", description="Programming language of the frontend code.")
    framework: Optional[str] = Field(None, description="Frontend framework used.")

class GeneratedApplication(BaseModel):
    """Represents a complete generated application."""
    application_name: str = Field(..., description="Name of the generated application.")
    architectural_plan: ArchitecturalPlan = Field(..., description="The architectural plan used for generation.")
    backend_code: List[BackendCode] = Field(default_factory=list, description="List of generated backend code files.")
    frontend_code: List[FrontendCode] = Field(default_factory=list, description="List of generated frontend code files.")
    # Add other components like database schemas, deployment scripts, etc.
