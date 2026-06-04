from app.controllers.vehicle_controller import router as vehicle_router
from app.controllers.parking_spot_controller import router as spot_router
from app.controllers.ticket_controller import router as ticket_router
from app.controllers.monthly_customer_controller import router as monthly_router

__all__ = ["vehicle_router", "spot_router", "ticket_router", "monthly_router"]
