from app.api.routes.vehicle_router import router as vehicle_router
from app.api.routes.parking_spot_router import router as spot_router
from app.api.routes.ticket_router import router as ticket_router
from app.api.routes.monthly_customer_router import router as monthly_router

__all__ = ["vehicle_router", "spot_router", "ticket_router", "monthly_router"]
