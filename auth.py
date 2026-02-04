"""
API 身份驗證模組
使用 Authorization Header (Bearer Token) 進行驗證
"""
from fastapi import Header, HTTPException, status
import os


def verify_token(authorization: str = Header(None)) -> str:
    """
    驗證 Authorization Header 中的 Bearer Token

    Args:
        authorization: HTTP Authorization Header (格式: "Bearer <token>")

    Returns:
        str: 驗證成功的 token

    Raises:
        HTTPException: 驗證失敗時拋出 401 或 403 錯誤
    """
    # 從環境變數取得有效的 token（預設值）
    # 支援多個 token，用逗號分隔
    DEFAULT_TOKEN = '0x718747ab68ce0f14bcc24f80a1d515194c591718'
    valid_tokens_str = os.getenv('VPP_API_TOKENS', DEFAULT_TOKEN)
    valid_tokens = [t.strip() for t in valid_tokens_str.split(',')]

    # 檢查是否提供 Authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 檢查格式是否正確 (Bearer <token>)
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header 格式錯誤，應為: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 提取 token
    token = authorization[7:]  # 移除 "Bearer " 前綴

    # 移除 valid_tokens 中的 "Bearer " 前綴（如果存在）
    valid_tokens = [t.replace('Bearer ', '') if t.startswith('Bearer ') else t for t in valid_tokens]

    # 驗證 token
    if token not in valid_tokens:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無效的 token，請檢查您的 Authorization header"
        )

    return token


def verify_token_optional(authorization: str = Header(None)) -> bool:
    """
    可選的 token 驗證（不強制要求）
    用於需要區分已驗證和未驗證使用者的場景

    Args:
        authorization: HTTP Authorization Header

    Returns:
        bool: True 表示已驗證，False 表示未驗證
    """
    if not authorization:
        return False

    try:
        verify_token(authorization)
        return True
    except HTTPException:
        return False