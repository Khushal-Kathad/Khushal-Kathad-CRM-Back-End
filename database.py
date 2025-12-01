from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event, exc, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# SQL query logging - set to WARNING to hide verbose queries, INFO to see all queries
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)  # Hiding SQL queries for cleaner logs

# Log connection attempt
logger.info("=" * 60)
logger.info("Initializing database connection to Azure SQL Server")
logger.info(f"Server: fastapidev.database.windows.net:1433")
logger.info(f"Database: swagatpillarcrm")
logger.info("=" * 60)

# Azure SQL connection using pymssql (no ODBC driver required - works on Databricks Apps)
SQLALCHEMY_DATABASE_URL = (
    "mssql+pymssql://maulik:Fastapiuser%401234@fastapidev.database.windows.net:1433/swagatpillarcrm"
)

# Create engine with Azure SQL optimized settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,               # Reduced pool size for Databricks Apps
    max_overflow=10,           # Reduced overflow
    pool_pre_ping=True,        # Verify connections before using them (CRITICAL for Azure SQL)
    pool_recycle=900,          # Recycle connections after 15 minutes
    pool_timeout=30,           # Wait up to 30 seconds for connection from pool
    echo=False,                # SQL query logging disabled for cleaner logs
    connect_args={"login_timeout": 60, "timeout": 60}  # pymssql timeout settings
)

# Add connection retry logic for transient errors
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Called when a new DB-API connection is created"""
    connection_record.info['pid'] = id(dbapi_conn)

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Called when a connection is retrieved from the pool"""
    pid = connection_record.info.get('pid')
    if pid != id(dbapi_conn):
        connection_record.info['pid'] = id(dbapi_conn)

# Handle disconnection errors gracefully
@event.listens_for(engine, "handle_error")
def handle_error(exception_context):
    """Handle specific database errors and enable retry logic"""
    if isinstance(exception_context.original_exception, exc.DBAPIError):
        # Check for connection-related errors
        error_code = str(exception_context.original_exception.orig)
        if any(code in error_code for code in ['08S01', '08001', '40613', '40197', '40501', '40540', '10053', '10054', '0x20']):
            # These are transient/connection errors - mark for retry
            exception_context.is_disconnect = True

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def test_database_connection():
    """
    Test database connection. Call this after app startup, not at import time.
    Returns True if connection successful, False otherwise.
    """
    try:
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
            return True
    except Exception as e:
        logger.error(f"Database connection FAILED: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Please check:")
        logger.error("  1. Azure SQL firewall allows Databricks Apps IP addresses")
        logger.error("  2. Database credentials are correct")
        logger.error("  3. Network connectivity to fastapidev.database.windows.net:1433")
        return False


def get_db():
    """
    Dependency for FastAPI routes to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

