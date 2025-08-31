"""
Deal model for TerraFlow land acquisition analysis.
Contains Pydantic data models and core financial calculations.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import pandas as pd


class LandInputs(BaseModel):
    """Land acquisition input parameters."""

    # Site Information
    site_name: str = Field(..., description="Name/identifier for the site")
    land_area_sqm: float = Field(..., gt=0, description="Total land area in square meters")
    asking_price: float = Field(..., gt=0, description="Land asking price in dollars")
    taxes_fees: float = Field(0.0, ge=0, description="Transfer taxes and fees")

    # Zoning and Development Constraints
    zoning: str = Field("Unknown", description="Zoning classification")
    far: Optional[float] = Field(None, gt=0, le=10, description="Floor Area Ratio")
    coverage: float = Field(..., gt=0, lt=1, description="Maximum site coverage ratio")
    max_floors: int = Field(1, ge=1, le=50, description="Maximum building floors")
    efficiency_ratio: float = Field(..., gt=0, lt=1, description="Net sellable / Gross area ratio")

    # Market Assumptions
    expected_sale_price_psm: float = Field(..., gt=0, description="Expected sale price per sqm")
    construction_cost_psm: float = Field(..., gt=0, description="Construction cost per sqm")
    soft_cost_pct: float = Field(..., gt=0, lt=1, description="Soft costs as % of hard costs")
    profit_target_pct: float = Field(..., gt=0, lt=1, description="Developer profit target %")

    # Optional Risk Factors
    financing_cost: float = Field(0.0, ge=0, description="Interest during construction")
    holding_period_months: int = Field(24, ge=1, le=120, description="Development timeline")
    months_to_sell: Optional[int] = Field(None, ge=1, le=120, description="Absorption period in months")

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("efficiency_ratio")
    @classmethod
    def validate_efficiency_ratio(cls, v):
        if not 0.6 <= v <= 0.95:
            raise ValueError("Efficiency ratio should be between 60% and 95%")
        return v

    @field_validator("profit_target_pct")
    @classmethod
    def validate_profit_target(cls, v):
        if not 0.05 <= v <= 0.50:
            raise ValueError("Profit target should be between 5% and 50%")
        return v


class CalculatedOutputs(BaseModel):
    """Calculated outputs from land deal analysis."""

    # Development Capacity
    gross_buildable_sqm: float = Field(..., description="Maximum buildable area")
    net_sellable_sqm: float = Field(..., description="Net sellable area")

    # Financial Metrics
    gdv: float = Field(..., description="Gross Development Value")
    hard_costs: float = Field(..., description="Construction costs")
    soft_costs: float = Field(..., description="Professional fees, permits etc")
    total_dev_cost: float = Field(..., description="Total development cost excluding land")
    required_profit: float = Field(..., description="Target developer profit")
    residual_land_value: float = Field(..., description="Maximum affordable land price")

    # Acquisition Metrics
    total_acquisition_cost: float = Field(..., description="Total land acquisition cost")
    land_psm: float = Field(..., description="Land price per square meter")
    land_per_buildable: float = Field(..., description="Land cost per buildable sqm")
    land_pct_gdv: float = Field(..., description="Land as percentage of GDV")
    
    # New KPIs
    acq_cost_per_land_sqm: Optional[float] = Field(None, description="Acquisition cost per total land area")
    acq_cost_per_gfa_sqm: Optional[float] = Field(None, description="Acquisition cost per buildable area")
    land_cost_per_nsa_sqm: Optional[float] = Field(None, description="Land cost per net sellable area")
    monthly_absorption_rate: Optional[float] = Field(None, description="Monthly absorption rate (fraction)")

    # Viability Indicators
    asking_vs_residual: float = Field(..., description="Asking price vs residual value")
    breakeven_sale_price: float = Field(..., description="Required sale price to break even")

    model_config = ConfigDict(validate_assignment=True)


class ViabilityScores(BaseModel):
    """Viability scoring and risk flags."""

    residual_score: str = Field(..., pattern="^(green|yellow|red)$")
    residual_status: str = Field(...)

    land_pct_score: str = Field(..., pattern="^(green|yellow|red)$")
    land_pct_status: str = Field(...)

    breakeven_score: str = Field(..., pattern="^(green|yellow|red)$")
    breakeven_status: str = Field(...)

    overall_score: str = Field(..., pattern="^(green|yellow|red)$")
    overall_status: str = Field(...)


class SensitivityAnalysis(BaseModel):
    """Sensitivity analysis results."""

    base_residual: float = Field(..., description="Base case residual land value")
    sales_down_10pct: float = Field(..., description="Residual if sales price -10%")
    costs_up_10pct: float = Field(..., description="Residual if costs +10%")
    sales_impact: float = Field(..., description="Impact of sales decrease")
    costs_impact: float = Field(..., description="Impact of cost increase")


class LandDeal(BaseModel):
    """Complete land deal analysis."""

    inputs: LandInputs
    outputs: Optional[CalculatedOutputs] = None
    viability: Optional[ViabilityScores] = None
    sensitivity: Optional[SensitivityAnalysis] = None

    model_config = ConfigDict(validate_assignment=True)

    def compute_outputs(self) -> "LandDeal":
        """
        Calculate all financial outputs from inputs.

        Returns:
            Self with computed outputs, viability scores, and sensitivity analysis
        """
        from modules.calculators.residual import calculate_development_capacity
        
        # Development Capacity Calculations
        capacity = calculate_development_capacity(
            land_area_sqm=self.inputs.land_area_sqm,
            far=self.inputs.far,
            coverage=self.inputs.coverage,
            max_floors=self.inputs.max_floors,
            efficiency_ratio=self.inputs.efficiency_ratio
        )
        
        gross_buildable_sqm = capacity.gross_buildable_sqm
        
        # NSA calculation
        net_sellable_sqm = capacity.net_sellable_sqm

        # Financial Calculations
        gdv = net_sellable_sqm * self.inputs.expected_sale_price_psm
        hard_costs = gross_buildable_sqm * self.inputs.construction_cost_psm
        soft_costs = hard_costs * self.inputs.soft_cost_pct
        total_dev_cost = hard_costs + soft_costs + self.inputs.financing_cost
        required_profit = gdv * self.inputs.profit_target_pct
        residual_land_value = gdv - total_dev_cost - required_profit

        # Acquisition Metrics
        total_acquisition_cost = self.inputs.asking_price + self.inputs.taxes_fees
        land_psm = self.inputs.asking_price / self.inputs.land_area_sqm
        land_per_buildable = self.inputs.asking_price / gross_buildable_sqm if gross_buildable_sqm > 0 else 0
        land_pct_gdv = (total_acquisition_cost / gdv * 100) if gdv > 0 else 0
        
        # New KPIs calculations
        acq_cost_per_land_sqm = self.inputs.asking_price / self.inputs.land_area_sqm if self.inputs.land_area_sqm else None
        acq_cost_per_gfa_sqm = self.inputs.asking_price / gross_buildable_sqm if gross_buildable_sqm else None
        land_cost_per_nsa_sqm = self.inputs.asking_price / net_sellable_sqm if net_sellable_sqm else None
        
        # Absorption calculation
        monthly_absorption_rate = None
        if self.inputs.months_to_sell and self.inputs.months_to_sell > 0:
            monthly_absorption_rate = 1.0 / self.inputs.months_to_sell

        # Viability Indicators
        asking_vs_residual = self.inputs.asking_price - residual_land_value
        breakeven_sale_price = (total_dev_cost + total_acquisition_cost) / net_sellable_sqm if net_sellable_sqm > 0 else 0

        # Store calculated outputs
        self.outputs = CalculatedOutputs(
            gross_buildable_sqm=gross_buildable_sqm,
            net_sellable_sqm=net_sellable_sqm,
            gdv=gdv,
            hard_costs=hard_costs,
            soft_costs=soft_costs,
            total_dev_cost=total_dev_cost,
            required_profit=required_profit,
            residual_land_value=residual_land_value,
            total_acquisition_cost=total_acquisition_cost,
            land_psm=land_psm,
            land_per_buildable=land_per_buildable,
            land_pct_gdv=land_pct_gdv,
            asking_vs_residual=asking_vs_residual,
            breakeven_sale_price=breakeven_sale_price,
            acq_cost_per_land_sqm=acq_cost_per_land_sqm,
            acq_cost_per_gfa_sqm=acq_cost_per_gfa_sqm,
            land_cost_per_nsa_sqm=land_cost_per_nsa_sqm,
            monthly_absorption_rate=monthly_absorption_rate,
        )

        # Calculate viability scores
        self._calculate_viability_scores()

        # Calculate sensitivity analysis
        self._calculate_sensitivity_analysis()

        return self

    def _calculate_viability_scores(self) -> None:
        """Calculate viability scores and risk flags."""
        if not self.outputs:
            raise ValueError("Must compute outputs first")

        # Score residual vs asking
        if self.outputs.residual_land_value > self.inputs.asking_price * 1.1:  # 10% buffer
            residual_score = "green"
            residual_status = "Healthy margin"
        elif self.outputs.residual_land_value > self.inputs.asking_price:
            residual_score = "yellow"
            residual_status = "Marginal"
        else:
            residual_score = "red"
            residual_status = "Over budget"

        # Score land % of GDV (typical range 15-25%)
        if 15 <= self.outputs.land_pct_gdv <= 25:
            land_pct_score = "green"
            land_pct_status = "Within norms"
        elif 10 <= self.outputs.land_pct_gdv < 15:
            land_pct_score = "green"
            land_pct_status = "Low land cost"
        elif 25 < self.outputs.land_pct_gdv <= 30:
            land_pct_score = "yellow"
            land_pct_status = "Above average"
        elif self.outputs.land_pct_gdv < 10:
            land_pct_score = "yellow"
            land_pct_status = "Very low land cost"
        else:
            land_pct_score = "red"
            land_pct_status = "Too high"

        # Score breakeven vs market (using expected sale price as market)
        breakeven_pct_market = (
            self.outputs.breakeven_sale_price / self.inputs.expected_sale_price_psm * 100
            if self.inputs.expected_sale_price_psm > 0
            else 100
        )

        if breakeven_pct_market < 80:
            breakeven_score = "green"
            breakeven_status = "Good buffer"
        elif breakeven_pct_market < 85:
            breakeven_score = "yellow"
            breakeven_status = "Tight margin"
        else:
            breakeven_score = "red"
            breakeven_status = "High risk"

        # Overall score
        scores = [residual_score, land_pct_score, breakeven_score]
        red_flags = scores.count("red")
        yellow_flags = scores.count("yellow")

        if red_flags == 0 and yellow_flags <= 1:
            overall_score = "green"
            overall_status = "Viable"
        elif red_flags == 0:
            overall_score = "yellow"
            overall_status = "Caution"
        else:
            overall_score = "red"
            overall_status = "High risk"

        self.viability = ViabilityScores(
            residual_score=residual_score,
            residual_status=residual_status,
            land_pct_score=land_pct_score,
            land_pct_status=land_pct_status,
            breakeven_score=breakeven_score,
            breakeven_status=breakeven_status,
            overall_score=overall_score,
            overall_status=overall_status,
        )

    def _calculate_sensitivity_analysis(self) -> None:
        """Calculate sensitivity scenarios."""
        if not self.outputs:
            raise ValueError("Must compute outputs first")

        base_residual = self.outputs.residual_land_value

        # Sales price -10% scenario
        reduced_gdv = self.outputs.net_sellable_sqm * (self.inputs.expected_sale_price_psm * 0.9)
        reduced_profit = reduced_gdv * self.inputs.profit_target_pct
        sales_down_residual = reduced_gdv - self.outputs.total_dev_cost - reduced_profit

        # Construction cost +10% scenario
        increased_hard_costs = self.outputs.hard_costs * 1.1
        increased_soft_costs = increased_hard_costs * self.inputs.soft_cost_pct
        increased_total_cost = increased_hard_costs + increased_soft_costs + self.inputs.financing_cost
        costs_up_residual = self.outputs.gdv - increased_total_cost - self.outputs.required_profit

        self.sensitivity = SensitivityAnalysis(
            base_residual=base_residual,
            sales_down_10pct=sales_down_residual,
            costs_up_10pct=costs_up_residual,
            sales_impact=sales_down_residual - base_residual,
            costs_impact=costs_up_residual - base_residual,
        )

    def to_summary_dict(self) -> Dict[str, Any]:
        """
        Convert deal to summary dictionary for display/export.

        Returns:
            Dictionary with formatted key metrics
        """
        if not self.outputs or not self.viability:
            raise ValueError("Must compute outputs first")

        return {
            "site_name": self.inputs.site_name,
            "land_area_sqm": f"{self.inputs.land_area_sqm:,.0f}",
            "asking_price": f"${self.inputs.asking_price:,.0f}",
            "residual_land_value": f"${self.outputs.residual_land_value:,.0f}",
            "land_pct_gdv": f"{self.outputs.land_pct_gdv:.1f}%",
            "breakeven_sale_price": f"${self.outputs.breakeven_sale_price:,.0f}",
            "overall_score": self.viability.overall_score,
            "overall_status": self.viability.overall_status,
        }


def create_deal_from_dict(data: Dict[str, Any]) -> LandDeal:
    """
    Create a LandDeal from dictionary data.

    Args:
        data: Dictionary containing land acquisition parameters

    Returns:
        LandDeal instance
    """
    inputs = LandInputs(**data)
    deal = LandDeal(inputs=inputs)
    return deal.compute_outputs()


def batch_process_deals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process multiple deals from a DataFrame.

    Args:
        df: DataFrame with deal input columns

    Returns:
        DataFrame with added output columns
    """
    results = []

    for _, row in df.iterrows():
        try:
            deal = create_deal_from_dict(row.to_dict())
            summary = deal.to_summary_dict()

            # Combine inputs and outputs
            result_row = row.to_dict()
            result_row.update(summary)
            result_row.update(
                {
                    "residual_land_value_num": deal.outputs.residual_land_value,
                    "land_pct_gdv_num": deal.outputs.land_pct_gdv,
                    "breakeven_sale_price_num": deal.outputs.breakeven_sale_price,
                    "processing_status": "success",
                }
            )

        except Exception as e:
            result_row = row.to_dict()
            result_row.update(
                {"processing_status": f"error: {str(e)}", "overall_score": "red", "overall_status": "Processing failed"}
            )

        results.append(result_row)

    return pd.DataFrame(results)
