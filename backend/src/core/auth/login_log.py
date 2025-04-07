"""
登录日志服务
负责记录用户登录行为和查询登录历史
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from core.auth.models import LoginLog, User


class LoginLogService:
    """登录日志服务类"""
    
    @staticmethod
    async def add_login_log(
        db: Session,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        login_status: bool = False,
        status_message: Optional[str] = None,
        captcha_verified: bool = False
    ) -> LoginLog:
        """添加登录日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            username: 用户名，如果user_id为空但提供了username，会尝试查找用户
            ip_address: 用户IP地址
            user_agent: 用户浏览器信息
            login_status: 登录是否成功
            status_message: 状态信息，比如失败原因
            captcha_verified: 是否通过验证码验证
            
        Returns:
            LoginLog: 创建的登录日志记录
        """
        # 如果没有提供user_id但提供了username，尝试查找用户
        if user_id is None and username:
            user = db.query(User).filter(User.username == username).first()
            if user:
                user_id = user.id
        
        # 创建登录日志记录
        login_log = LoginLog(
            user_id=user_id if user_id else None,
            ip_address=ip_address,
            user_agent=user_agent,
            login_status=login_status,
            status_message=status_message,
            captcha_verified=captcha_verified
        )
        
        # 保存到数据库
        db.add(login_log)
        db.commit()
        db.refresh(login_log)
        
        return login_log
    
    @staticmethod
    async def get_user_login_logs(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[LoginLog]:
        """获取用户登录日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数上限
            
        Returns:
            List[LoginLog]: 登录日志列表
        """
        return db.query(LoginLog).filter(
            LoginLog.user_id == user_id
        ).order_by(
            desc(LoginLog.login_time)
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_recent_logins(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[bool] = None
    ) -> List[LoginLog]:
        """获取最近的登录日志
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数上限
            status_filter: 登录状态过滤
            
        Returns:
            List[LoginLog]: 登录日志列表
        """
        query = db.query(LoginLog)
        
        # 应用状态过滤
        if status_filter is not None:
            query = query.filter(LoginLog.login_status == status_filter)
        
        return query.order_by(
            desc(LoginLog.login_time)
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_login_statistics(
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取登录统计信息
        
        Args:
            db: 数据库会话
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        query = db.query(LoginLog)
        
        # 应用时间过滤
        if start_time:
            query = query.filter(LoginLog.login_time >= start_time)
        if end_time:
            query = query.filter(LoginLog.login_time <= end_time)
        
        # 总登录次数
        total_logins = query.count()
        
        # 成功登录次数
        success_logins = query.filter(LoginLog.login_status == True).count()
        
        # 失败登录次数
        failed_logins = query.filter(LoginLog.login_status == False).count()
        
        # 验证码验证情况
        captcha_verified = query.filter(LoginLog.captcha_verified == True).count()
        
        return {
            "total_logins": total_logins,
            "success_logins": success_logins,
            "failed_logins": failed_logins,
            "success_rate": (success_logins / total_logins * 100) if total_logins > 0 else 0,
            "captcha_verified": captcha_verified,
            "captcha_rate": (captcha_verified / total_logins * 100) if total_logins > 0 else 0
        } 