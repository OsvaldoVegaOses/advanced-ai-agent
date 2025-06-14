"""
Database Configuration and Management
Advanced PostgreSQL setup with async support and connection pooling
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import asyncpg
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
import redis.asyncio as redis

from core.config import settings
from core.logging import get_logger
from core.exceptions import DatabaseConnectionError

logger = get_logger(__name__)

# SQLAlchemy Base
Base = declarative_base()
metadata = MetaData()

# Database engines
async_engine = None
sync_engine = None
async_session_factory = None
redis_client = None


async def init_db() -> None:
    """Initialize database connections and create tables"""
    global async_engine, sync_engine, async_session_factory, redis_client
    
    try:
        logger.info("Initializing database connections...")
        
        # Create async engine
        async_engine = create_async_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.DEBUG,
            pool_size=settings.database_config["pool_size"],
            max_overflow=settings.database_config["max_overflow"],
            pool_pre_ping=True,
            poolclass=NullPool if settings.ENVIRONMENT == "test" else None
        )
        
        # Create sync engine for migrations
        sync_engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=settings.database_config["pool_size"],
            max_overflow=settings.database_config["max_overflow"],
            pool_pre_ping=True
        )
        
        # Create session factory
        async_session_factory = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Initialize Redis
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connections
        await test_database_connection()
        await test_redis_connection()
        
        logger.info("✅ Database connections initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise DatabaseConnectionError(f"Database initialization failed: {str(e)}")


async def test_database_connection() -> None:
    """Test database connection"""
    try:
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ PostgreSQL connection test successful")
    except Exception as e:
        logger.error(f"PostgreSQL connection test failed: {e}")
        raise


async def test_redis_connection() -> None:
    """Test Redis connection"""
    try:
        await redis_client.ping()
        logger.info("✅ Redis connection test successful")
    except Exception as e:
        logger.error(f"Redis connection test failed: {e}")
        raise


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with automatic cleanup"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Get Redis client with connection management"""
    try:
        yield redis_client
    except Exception as e:
        logger.error(f"Redis operation failed: {e}")
        raise


class DatabaseManager:
    """Database operations manager with advanced features"""
    
    def __init__(self):
        self.logger = get_logger("database")
    
    async def execute_query(self, query: str, params: dict = None) -> list:
        """Execute raw SQL query safely"""
        async with get_db_session() as session:
            try:
                result = await session.execute(query, params or {})
                return result.fetchall()
            except Exception as e:
                self.logger.error(f"Query execution failed: {e}")
                raise
    
    async def bulk_insert(self, model_class, data: list) -> int:
        """Efficient bulk insert operation"""
        async with get_db_session() as session:
            try:
                session.add_all([model_class(**item) for item in data])
                await session.flush()
                return len(data)
            except Exception as e:
                self.logger.error(f"Bulk insert failed: {e}")
                raise
    
    async def health_check(self) -> dict:
        """Comprehensive database health check"""
        health_status = {
            "postgres": {"status": "unknown", "latency_ms": None},
            "redis": {"status": "unknown", "latency_ms": None}
        }
        
        # PostgreSQL health check
        try:
            import time
            start_time = time.time()
            async with get_db_session() as session:
                await session.execute("SELECT 1")
            health_status["postgres"] = {
                "status": "healthy",
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            health_status["postgres"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Redis health check
        try:
            start_time = time.time()
            async with get_redis() as redis_conn:
                await redis_conn.ping()
            health_status["redis"] = {
                "status": "healthy",
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            health_status["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return health_status
    
    async def get_connection_stats(self) -> dict:
        """Get database connection pool statistics"""
        try:
            stats = {
                "pool_size": async_engine.pool.size(),
                "checked_in": async_engine.pool.checkedin(),
                "checked_out": async_engine.pool.checkedout(),
                "overflow": async_engine.pool.overflow(),
                "invalid": async_engine.pool.invalid()
            }
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get connection stats: {e}")
            return {}


class CacheManager:
    """Redis cache manager with advanced features"""
    
    def __init__(self):
        self.logger = get_logger("cache")
        self.default_ttl = settings.CACHE_TTL_SECONDS
    
    async def get(self, key: str, default=None):
        """Get value from cache"""
        try:
            async with get_redis() as redis_conn:
                value = await redis_conn.get(key)
                return value if value is not None else default
        except Exception as e:
            self.logger.error(f"Cache get failed for key {key}: {e}")
            return default
    
    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set value in cache with TTL"""
        try:
            async with get_redis() as redis_conn:
                await redis_conn.setex(key, ttl or self.default_ttl, value)
                return True
        except Exception as e:
            self.logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            async with get_redis() as redis_conn:
                result = await redis_conn.delete(key)
                return bool(result)
        except Exception as e:
            self.logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            async with get_redis() as redis_conn:
                result = await redis_conn.exists(key)
                return bool(result)
        except Exception as e:
            self.logger.error(f"Cache exists check failed for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache"""
        try:
            async with get_redis() as redis_conn:
                return await redis_conn.incr(key, amount)
        except Exception as e:
            self.logger.error(f"Cache increment failed for key {key}: {e}")
            return 0
    
    async def set_json(self, key: str, data: dict, ttl: int = None) -> bool:
        """Store JSON data in cache"""
        import json
        try:
            json_data = json.dumps(data)
            return await self.set(key, json_data, ttl)
        except Exception as e:
            self.logger.error(f"Cache set_json failed for key {key}: {e}")
            return False
    
    async def get_json(self, key: str, default=None) -> dict:
        """Get JSON data from cache"""
        import json
        try:
            value = await self.get(key)
            if value:
                return json.loads(value)
            return default
        except Exception as e:
            self.logger.error(f"Cache get_json failed for key {key}: {e}")
            return default
    
    async def get_or_set(self, key: str, fetch_func, ttl: int = None):
        """Get from cache or fetch and set if not exists"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Fetch new value
        if asyncio.iscoroutinefunction(fetch_func):
            new_value = await fetch_func()
        else:
            new_value = fetch_func()
        
        # Set in cache
        if new_value is not None:
            if isinstance(new_value, dict):
                await self.set_json(key, new_value, ttl)
            else:
                await self.set(key, str(new_value), ttl)
        
        return new_value
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            async with get_redis() as redis_conn:
                keys = await redis_conn.keys(pattern)
                if keys:
                    return await redis_conn.delete(*keys)
                return 0
        except Exception as e:
            self.logger.error(f"Cache clear_pattern failed for pattern {pattern}: {e}")
            return 0


class SessionManager:
    """Conversation session manager with Redis backend"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.session_prefix = "session:"
        self.session_ttl = settings.CONVERSATION_TIMEOUT_MINUTES * 60
        self.logger = get_logger("session")
    
    async def create_session(self, session_id: str, user_data: dict = None) -> bool:
        """Create new conversation session"""
        session_data = {
            "session_id": session_id,
            "created_at": asyncio.get_event_loop().time(),
            "last_activity": asyncio.get_event_loop().time(),
            "user_data": user_data or {},
            "conversation_state": "greeting",
            "messages": [],
            "context": {}
        }
        
        key = f"{self.session_prefix}{session_id}"
        success = await self.cache.set_json(key, session_data, self.session_ttl)
        
        if success:
            self.logger.info(f"Session created: {session_id}")
        else:
            self.logger.error(f"Failed to create session: {session_id}")
        
        return success
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get conversation session data"""
        key = f"{self.session_prefix}{session_id}"
        session_data = await self.cache.get_json(key)
        
        if session_data:
            # Update last activity
            session_data["last_activity"] = asyncio.get_event_loop().time()
            await self.cache.set_json(key, session_data, self.session_ttl)
        
        return session_data
    
    async def update_session(self, session_id: str, updates: dict) -> bool:
        """Update conversation session data"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
        
        session_data.update(updates)
        session_data["last_activity"] = asyncio.get_event_loop().time()
        
        key = f"{self.session_prefix}{session_id}"
        return await self.cache.set_json(key, session_data, self.session_ttl)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete conversation session"""
        key = f"{self.session_prefix}{session_id}"
        success = await self.cache.delete(key)
        
        if success:
            self.logger.info(f"Session deleted: {session_id}")
        
        return success
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            async with get_redis() as redis_conn:
                # Get all session keys
                keys = await redis_conn.keys(f"{self.session_prefix}*")
                expired_count = 0
                current_time = asyncio.get_event_loop().time()
                
                for key in keys:
                    session_data = await self.cache.get_json(key.decode())
                    if session_data:
                        last_activity = session_data.get("last_activity", 0)
                        if current_time - last_activity > self.session_ttl:
                            await self.cache.delete(key.decode())
                            expired_count += 1
                
                if expired_count > 0:
                    self.logger.info(f"Cleaned up {expired_count} expired sessions")
                
                return expired_count
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {e}")
            return 0


# Initialize managers
db_manager = DatabaseManager()
cache_manager = CacheManager()
session_manager = SessionManager()


async def close_db_connections():
    """Close all database connections"""
    global async_engine, sync_engine, redis_client
    
    try:
        if redis_client:
            await redis_client.close()
        
        if async_engine:
            await async_engine.dispose()
        
        if sync_engine:
            sync_engine.dispose()
        
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session"""
    async with get_db_session() as session:
        yield session


async def get_cache() -> CacheManager:
    """FastAPI dependency for cache manager"""
    return cache_manager


async def get_session_mgr() -> SessionManager:
    """FastAPI dependency for session manager"""
    return session_manager