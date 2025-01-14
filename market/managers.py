from typing import TYPE_CHECKING, Any

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import QuerySet

if TYPE_CHECKING:
    from market.models import Market, Service, ServiceMaterial
    from users.models.reformer import Reformer


class MarketManager(models.Manager):

    def check_if_market_exists(self, reformer: "Reformer") -> bool:
        return self.model.objects.filter(reformer=reformer).exists()

    def get_market_by_reformer(self, reformer: "Reformer") -> "Market":
        market: "Market" = self.model.objects.filter(reformer=reformer).first()
        if not market:
            raise ObjectDoesNotExist("Market not found for this reformer")

        return market

    def get_market_by_user_related_to_reformer(self, user) -> "Market":
        market: "Market" = (
            self.model.objects.filter(reformer__user=user)
            .select_related("reformer")
            .first()
        )
        if not market:
            raise ObjectDoesNotExist("Market not found for this user")

        return market

    def get_market_by_market_uuid(self, market_uuid: str) -> "Market":
        market: "Market" = self.model.objects.filter(market_uuid=market_uuid).first()
        if not market:
            raise ObjectDoesNotExist("Market not found for this market_uuid")

        return market

    def get_market_by_market_uuid_related_to_reformer(
        self, market_uuid: str
    ) -> "Market":
        market: "Market" = (
            self.model.objects.filter(market_uuid=market_uuid)
            .select_related("reformer")
            .first()
        )
        if not market:
            raise ObjectDoesNotExist("Market not found for this market_uuid")

        return market


class ServiceManager(models.Manager):

    def get_all_service_queryset(self) -> QuerySet:
        queryset: QuerySet = (
            self.model.objects.select_related(
                "market", "market__reformer", "market__reformer__user"
            )
            .prefetch_related(
                "service_style",
                "service_image",
                "service_material",
                "service_option",
                "service_option__service_option_image",
                "market__reformer__reformer_education",
                "market__reformer__reformer_certification",
                "market__reformer__reformer_awards",
                "market__reformer__reformer_career",
                "market__reformer__reformer_freelancer",
            )
            .all()
        )
        if not queryset.exists():
            raise ObjectDoesNotExist("There are no services in the database")
        return queryset

    def get_service_queryset_by_market_uuid_with_temporary(
        self, market_uuid: str, temporary: str
    ) -> QuerySet:
        queryset: QuerySet = (
            self.model.objects.filter(
                market__market_uuid=market_uuid, temporary=temporary
            )
            .select_related(
                "market__reformer__user",
            )
            .prefetch_related(
                "market__reformer__reformer_education",
                "market__reformer__reformer_certification",
                "market__reformer__reformer_awards",
                "market__reformer__reformer_career",
                "market__reformer__reformer_freelancer",
                "service_option__service_option_image",
                "service_material",
                "service_style",
                "service_image",
            )
        )
        if not queryset.exists():
            raise ObjectDoesNotExist("Service not found")

        return queryset


class ServiceMaterialManager(models.Manager):
    def get_service_material_by_material_uuid(self, material_uuid) -> "ServiceMaterial":
        service_material: "ServiceMaterial" = self.model.objects.filter(
            material_uuid=material_uuid
        ).first()
        if not service_material:
            raise ObjectDoesNotExist("Service material not found")

        return service_material
