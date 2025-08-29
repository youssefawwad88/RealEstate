"""
Zoning and permit validation with country-specific rules.
Generates validation flags and warnings based on regulatory constraints.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .registry import RuleSet, ZoningRules


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Single validation issue."""
    
    severity: ValidationSeverity
    category: str  # "zoning", "permits", "financing", etc.
    code: str     # Unique issue code
    message: str  # Human readable description
    field: Optional[str] = None  # Field that caused the issue
    value: Optional[Any] = None  # Problematic value
    suggestion: Optional[str] = None  # Suggested fix


@dataclass
class ValidationReport:
    """Complete validation report."""
    
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    
    def add_issue(self, issue: ValidationIssue):
        """Add validation issue to report."""
        self.issues.append(issue)
        
        if issue.severity in [ValidationSeverity.WARNING]:
            self.warnings.append(issue)
        elif issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
            self.errors.append(issue)
            self.is_valid = False
    
    def get_critical_errors(self) -> List[ValidationIssue]:
        """Get only critical errors that prevent processing."""
        return [issue for issue in self.errors if issue.severity == ValidationSeverity.CRITICAL]
    
    def summary(self) -> Dict[str, int]:
        """Get summary counts by severity."""
        counts = {severity.value: 0 for severity in ValidationSeverity}
        for issue in self.issues:
            counts[issue.severity.value] += 1
        return counts


class ZoningValidator:
    """Validates development parameters against zoning rules."""
    
    def __init__(self, ruleset: RuleSet):
        self.ruleset = ruleset
    
    def validate_zoning_compliance(
        self,
        zoning_code: str,
        land_area_sqm: float,
        far: float,
        coverage: float,
        max_floors: int,
        building_height_m: Optional[float] = None,
        setbacks: Optional[Dict[str, float]] = None
    ) -> ValidationReport:
        """
        Validate development parameters against zoning rules.
        
        Args:
            zoning_code: Zoning classification code
            land_area_sqm: Total land area in square meters
            far: Proposed Floor Area Ratio
            coverage: Proposed site coverage ratio
            max_floors: Proposed number of floors
            building_height_m: Proposed building height in meters
            setbacks: Dict of setback measurements {"front": x, "side": y, "rear": z}
            
        Returns:
            ValidationReport with compliance issues
        """
        report = ValidationReport(is_valid=True)
        
        # Get zoning rules
        zoning_rules = self.ruleset.get_zoning(zoning_code)
        if not zoning_rules:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="zoning",
                code="ZONING_NOT_FOUND",
                message=f"Zoning code '{zoning_code}' not found in {self.ruleset.country_code} regulations",
                field="zoning",
                value=zoning_code,
                suggestion=f"Available zones: {list(self.ruleset.zoning_rules.keys())}"
            ))
            return report
        
        # Validate FAR
        if far > zoning_rules.far_max:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="zoning",
                code="FAR_EXCEEDED",
                message=f"FAR {far:.2f} exceeds maximum {zoning_rules.far_max:.2f} for {zoning_rules.name}",
                field="far",
                value=far,
                suggestion=f"Reduce FAR to maximum {zoning_rules.far_max:.2f}"
            ))
        elif far > zoning_rules.far_max * 0.9:  # Warning at 90% of max
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="zoning",
                code="FAR_HIGH",
                message=f"FAR {far:.2f} is close to maximum {zoning_rules.far_max:.2f}",
                field="far",
                value=far,
                suggestion="Consider reducing FAR for approval certainty"
            ))
        
        # Validate coverage
        if coverage > zoning_rules.coverage_max:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="zoning",
                code="COVERAGE_EXCEEDED",
                message=f"Coverage {coverage:.1%} exceeds maximum {zoning_rules.coverage_max:.1%}",
                field="coverage", 
                value=coverage,
                suggestion=f"Reduce coverage to maximum {zoning_rules.coverage_max:.1%}"
            ))
        
        # Validate floors
        if max_floors > zoning_rules.floors_max:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="zoning",
                code="FLOORS_EXCEEDED",
                message=f"Floors {max_floors} exceeds maximum {zoning_rules.floors_max}",
                field="max_floors",
                value=max_floors,
                suggestion=f"Reduce floors to maximum {zoning_rules.floors_max}"
            ))
        
        # Validate height if provided
        if building_height_m and building_height_m > zoning_rules.height_max_m:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="zoning",
                code="HEIGHT_EXCEEDED",
                message=f"Height {building_height_m}m exceeds maximum {zoning_rules.height_max_m}m",
                field="building_height_m",
                value=building_height_m,
                suggestion=f"Reduce height to maximum {zoning_rules.height_max_m}m"
            ))
        
        # Validate setbacks if provided
        if setbacks:
            required_setbacks = {
                "front": zoning_rules.setback_front_m,
                "side": zoning_rules.setback_side_m,
                "rear": zoning_rules.setback_rear_m
            }
            
            for direction, provided in setbacks.items():
                required = required_setbacks.get(direction)
                if required and provided < required:
                    report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="zoning",
                        code="SETBACK_INSUFFICIENT",
                        message=f"{direction.title()} setback {provided}m is less than required {required}m",
                        field=f"setback_{direction}",
                        value=provided,
                        suggestion=f"Increase {direction} setback to minimum {required}m"
                    ))
        
        # Check parking requirements
        gross_buildable = land_area_sqm * far
        if gross_buildable > 0:
            if "residential" in zoning_rules.name.lower():
                # Estimate units (assuming 80 sqm per unit average)
                estimated_units = (gross_buildable * 0.85) / 80  # 85% efficiency, 80 sqm/unit
                required_parking = estimated_units * zoning_rules.parking_ratio
                
                report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="parking",
                    code="PARKING_REQUIREMENT",
                    message=f"Estimated parking requirement: {required_parking:.0f} spaces ({zoning_rules.parking_ratio:.1f} per unit)",
                    suggestion="Verify parking can be accommodated on site"
                ))
            else:
                # Commercial parking per 100 sqm
                required_parking_per_100sqm = zoning_rules.parking_ratio
                report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="parking",
                    code="PARKING_REQUIREMENT",
                    message=f"Parking requirement: {required_parking_per_100sqm:.1f} spaces per 100 sqm GFA",
                    suggestion="Verify parking can be accommodated on site"
                ))
        
        return report
    
    def validate_mixed_use_requirements(
        self,
        zoning_code: str,
        residential_pct: float,
        commercial_pct: float
    ) -> ValidationReport:
        """Validate mixed-use component requirements."""
        report = ValidationReport(is_valid=True)
        
        zoning_rules = self.ruleset.get_zoning(zoning_code)
        if not zoning_rules:
            return report  # Skip if zoning not found
        
        # Check minimum residential component
        if zoning_rules.residential_component_min > 0:
            if residential_pct < zoning_rules.residential_component_min:
                report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="mixed_use",
                    code="INSUFFICIENT_RESIDENTIAL",
                    message=f"Residential component {residential_pct:.1%} below required minimum {zoning_rules.residential_component_min:.1%}",
                    field="residential_pct",
                    value=residential_pct,
                    suggestion=f"Increase residential component to minimum {zoning_rules.residential_component_min:.1%}"
                ))
        
        # Check minimum commercial component  
        if zoning_rules.commercial_component_min > 0:
            if commercial_pct < zoning_rules.commercial_component_min:
                report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="mixed_use", 
                    code="INSUFFICIENT_COMMERCIAL",
                    message=f"Commercial component {commercial_pct:.1%} below required minimum {zoning_rules.commercial_component_min:.1%}",
                    field="commercial_pct",
                    value=commercial_pct,
                    suggestion=f"Increase commercial component to minimum {zoning_rules.commercial_component_min:.1%}"
                ))
        
        return report


class PermitValidator:
    """Validates permit and approval requirements."""
    
    def __init__(self, ruleset: RuleSet):
        self.ruleset = ruleset
    
    def validate_permit_requirements(
        self,
        gross_buildable_sqm: float,
        floors: int,
        foreign_ownership: bool = False,
        development_type: str = "residential"
    ) -> ValidationReport:
        """
        Validate permit and approval requirements.
        
        Args:
            gross_buildable_sqm: Gross buildable area
            floors: Number of floors
            foreign_ownership: Whether foreign ownership is involved
            development_type: Type of development
            
        Returns:
            ValidationReport with permit requirements
        """
        report = ValidationReport(is_valid=True)
        
        # Foreign ownership validation
        if foreign_ownership and not self.ruleset.country_rules.foreign_ownership_allowed:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="permits",
                code="FOREIGN_OWNERSHIP_RESTRICTED",
                message="Foreign ownership is not permitted in this jurisdiction",
                field="foreign_ownership",
                value=True,
                suggestion="Explore local partnership structures"
            ))
        
        if foreign_ownership and self.ruleset.country_rules.max_foreign_ownership_pct < 1.0:
            max_pct = self.ruleset.country_rules.max_foreign_ownership_pct
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="permits",
                code="FOREIGN_OWNERSHIP_LIMITED",
                message=f"Foreign ownership limited to {max_pct:.0%}",
                suggestion=f"Structure ownership to comply with {max_pct:.0%} limit"
            ))
        
        # Building permit requirements (always required)
        report.add_issue(ValidationIssue(
            severity=ValidationSeverity.INFO,
            category="permits",
            code="BUILDING_PERMIT_REQUIRED",
            message="Building permit required for construction",
            suggestion="Allow for permit processing time in project schedule"
        ))
        
        # Environmental clearance
        if gross_buildable_sqm > 1000:  # Threshold for environmental review
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="permits",
                code="ENVIRONMENTAL_CLEARANCE_REQUIRED",
                message="Environmental clearance likely required for large developments",
                suggestion="Engage environmental consultant early in process"
            ))
        
        # Elevator requirements based on floors
        if floors >= 4:  # Typically required above 3-4 floors
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="permits",
                code="ELEVATOR_REQUIRED",
                message=f"Elevator required for {floors}-floor building",
                suggestion="Include elevator costs and space in design"
            ))
        
        # Fire safety requirements
        if floors >= 3 or gross_buildable_sqm > 500:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="permits",
                code="FIRE_SAFETY_APPROVAL_REQUIRED",
                message="Fire safety approval required",
                suggestion="Engage fire safety consultant for design compliance"
            ))
        
        return report


class FinancingValidator:
    """Validates financing feasibility and requirements."""
    
    def __init__(self, ruleset: RuleSet):
        self.ruleset = ruleset
    
    def validate_financing_feasibility(
        self,
        equity_pct: float,
        ltv_ratio: float,
        foreign_buyer: bool = False
    ) -> ValidationReport:
        """
        Validate financing parameters against regulatory limits.
        
        Args:
            equity_pct: Equity percentage (1 - LTV)
            ltv_ratio: Loan-to-value ratio
            foreign_buyer: Whether buyer is foreign
            
        Returns:
            ValidationReport with financing issues
        """
        report = ValidationReport(is_valid=True)
        
        # Validate LTV ratio
        max_ltv = self.ruleset.country_rules.max_ltv_ratio
        if ltv_ratio > max_ltv:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="financing",
                code="LTV_EXCEEDED",
                message=f"LTV {ltv_ratio:.1%} exceeds maximum {max_ltv:.1%}",
                field="ltv_ratio",
                value=ltv_ratio,
                suggestion=f"Reduce LTV to maximum {max_ltv:.1%} or increase equity"
            ))
        
        # Validate minimum equity
        min_equity = self.ruleset.country_rules.min_equity_requirement
        if equity_pct < min_equity:
            report.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="financing",
                code="INSUFFICIENT_EQUITY",
                message=f"Equity {equity_pct:.1%} below minimum {min_equity:.1%}",
                field="equity_pct",
                value=equity_pct,
                suggestion=f"Increase equity to minimum {min_equity:.1%}"
            ))
        
        # Foreign buyer specific rules (UAE example)
        if foreign_buyer and self.ruleset.country_code == "UAE":
            if hasattr(self.ruleset.country_rules, 'non_resident_max_ltv'):
                foreign_max_ltv = 0.60  # Typically lower for non-residents
                if ltv_ratio > foreign_max_ltv:
                    report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="financing",
                        code="FOREIGN_LTV_EXCEEDED",
                        message=f"Non-resident LTV {ltv_ratio:.1%} exceeds maximum {foreign_max_ltv:.1%}",
                        field="ltv_ratio",
                        value=ltv_ratio,
                        suggestion=f"Reduce LTV to {foreign_max_ltv:.1%} for non-resident financing"
                    ))
        
        return report


def validate_deal_comprehensive(
    ruleset: RuleSet,
    deal_inputs: Dict[str, Any]
) -> ValidationReport:
    """
    Comprehensive validation of a land deal against all applicable rules.
    
    Args:
        ruleset: Country-specific ruleset
        deal_inputs: Dictionary of deal input parameters
        
    Returns:
        ValidationReport with all validation issues
    """
    combined_report = ValidationReport(is_valid=True)
    
    # Zoning validation
    zoning_validator = ZoningValidator(ruleset)
    if "zoning" in deal_inputs and "land_area_sqm" in deal_inputs:
        zoning_report = zoning_validator.validate_zoning_compliance(
            zoning_code=deal_inputs["zoning"],
            land_area_sqm=deal_inputs["land_area_sqm"],
            far=deal_inputs.get("far", 1.0),
            coverage=deal_inputs.get("coverage", 0.5),
            max_floors=deal_inputs.get("max_floors", 1)
        )
        
        for issue in zoning_report.issues:
            combined_report.add_issue(issue)
    
    # Permit validation
    permit_validator = PermitValidator(ruleset)
    if "land_area_sqm" in deal_inputs and "far" in deal_inputs:
        gross_buildable = deal_inputs["land_area_sqm"] * deal_inputs["far"]
        permit_report = permit_validator.validate_permit_requirements(
            gross_buildable_sqm=gross_buildable,
            floors=deal_inputs.get("max_floors", 1),
            foreign_ownership=deal_inputs.get("foreign_ownership", False)
        )
        
        for issue in permit_report.issues:
            combined_report.add_issue(issue)
    
    # Financing validation  
    financing_validator = FinancingValidator(ruleset)
    if "ltv_ratio" in deal_inputs:
        financing_report = financing_validator.validate_financing_feasibility(
            equity_pct=1.0 - deal_inputs.get("ltv_ratio", 0.7),
            ltv_ratio=deal_inputs.get("ltv_ratio", 0.7),
            foreign_buyer=deal_inputs.get("foreign_buyer", False)
        )
        
        for issue in financing_report.issues:
            combined_report.add_issue(issue)
    
    return combined_report