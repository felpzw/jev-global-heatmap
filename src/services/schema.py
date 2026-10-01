"""Contrato único entre o modelo, a visualização e a interface."""

import pycountry
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CountryHeatmap(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", str_strip_whitespace=True)

    iso_alpha_3: str = Field(pattern=r"^[A-Z]{3}$", description="Código ISO 3166-1 alpha-3 existente")
    heat_score: float = Field(ge=0, le=100, allow_inf_nan=False)
    context_summary: str = Field(min_length=1, max_length=300)

    @field_validator("iso_alpha_3")
    @classmethod
    def existing_country(cls, value: str) -> str:
        if pycountry.countries.get(alpha_3=value) is None:
            raise ValueError("Código ISO 3166-1 alpha-3 inexistente")
        return value


class HeatmapResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    # Empty means insufficient context, not a world full of zero scores.
    countries: list[CountryHeatmap] = Field(max_length=249)

    @field_validator("countries")
    @classmethod
    def unique_countries(cls, value: list[CountryHeatmap]) -> list[CountryHeatmap]:
        codes = [country.iso_alpha_3 for country in value]
        if len(codes) != len(set(codes)):
            raise ValueError("Países duplicados na resposta")
        return value
