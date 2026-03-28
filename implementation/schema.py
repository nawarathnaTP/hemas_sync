from pydantic import BaseModel, Field
from typing import ClassVar, List, Optional


class SOPRole(BaseModel):
    """A person/role involved in the process."""
    title: str = Field(..., description="Job title or role name, e.g. 'Shift Supervisor'")
    responsibility: str = Field(..., description="What this person does in this process")


class SOPStep(BaseModel):
    """A single procedural step in the SOP."""
    step_number: int
    action: str = Field(..., description="What the person does at this step")
    responsible_role: str = Field(..., description="Who performs this step")
    tools_or_systems: Optional[str] = Field(None, description="Any tools, software, or equipment used")


class HemasSOP(BaseModel):
    """
    Full SOP document model — mirrors the Hemas SOP Word template.
    Fields set to None will trigger an iterative follow-up question.
    """
    # Section 1: Header Info
    sop_title: Optional[str] = Field(None, description="Name of this procedure")
    department: Optional[str] = Field(None, description="Department or SBU this SOP belongs to")
    sbu: Optional[str] = Field(None, description="Strategic Business Unit (e.g. Hemas Mobility, Morison Manufacturing)")

    # Section 2: Procedure Overview
    purpose: Optional[str] = Field(None, description="Why this procedure exists and what it achieves")
    scope: Optional[str] = Field(None, description="Which teams, locations, or situations this SOP applies to")
    target_population: Optional[str] = Field(None, description="Who follows this procedure")

    # Section 3: Roles
    roles: Optional[List[SOPRole]] = Field(None, description="All roles involved and their responsibilities")

    # Section 4: Step-by-step procedure
    steps: Optional[List[SOPStep]] = Field(None, description="Ordered list of procedural steps")
    tools_required: Optional[List[str]] = Field(None, description="All tools, systems, or equipment referenced")

    # Section 5: Compliance (CRITICAL — must not be None)
    failure_protocols: Optional[str] = Field(
        None,
        description="What happens if the process fails or the system goes down",
    )
    backup_personnel: Optional[str] = Field(
        None,
        description="Who takes over if the primary responsible person is unavailable",
    )
    escalation_path: Optional[str] = Field(
        None,
        description="Who to contact if a step cannot be completed",
    )

    REQUIRED_FIELDS: ClassVar[List[str]] = [
        "sop_title",
        "department",
        "purpose",
        "scope",
        "target_population",
        "roles",
        "steps",
        "failure_protocols",
        "backup_personnel",
        "escalation_path",
    ]

    def get_missing_fields(self) -> List[str]:
        """Returns a list of required fields that are still None."""
        missing = []
        for field in self.REQUIRED_FIELDS:
            value = getattr(self, field)
            if value is None:
                missing.append(field)
        return missing

    def is_complete(self) -> bool:
        """Returns True only when all required fields are filled."""
        return len(self.get_missing_fields()) == 0
