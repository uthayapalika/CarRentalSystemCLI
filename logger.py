import logging
import os

log_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "car_rental_system.log"
)

logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)