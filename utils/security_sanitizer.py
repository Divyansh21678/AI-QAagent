import re

class SecuritySanitizer:
    @staticmethod
    def sanitize_input_text(text: str) -> str:
        """
        Cleans and normalizes text inputs to prevent prompt injections,
        removes hazardous control characters, and strips credential leaks.
        """
        if not text:
            return ""
            
        # 1. Strip suspicious command patterns (Basic Prompt Injection defense)
        injection_patterns = [
            r"(?i)forget\s+(?:all\s+)?previous\s+instructions",
            r"(?i)ignore\s+(?:all\s+)?prior\s+directives",
            r"(?i)system\s+prompt\s*(?:disclosure|leak|show)",
            r"(?i)you\s+are\s+now\s+an\s+unrestricted"
        ]
        
        sanitized = text
        for pattern in injection_patterns:
            sanitized = re.sub(pattern, "[Security Flag: Instruction Overriding Blocked]", sanitized)
            
        # 2. Strict Redaction for Standalone Tokens (Fixes the Bearer token bypass)
        # Matches dynamic headers like token_live_xyz, live_key_xyz, test_key_xyz directly in lines
        sanitized = re.sub(r"\b(token|key)_(live|test)_[a-zA-Z0-9]{16,}\b", "[REDACTED_BY_SECURITY_GUARD]", sanitized)
            
        # 3. Block and strip standard structural credential leak patterns (API Keys, Bearer Tokens with assignment indicators)
        sanitized = re.sub(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[a-zA-Z0-9_\-\.]{16,}", r"\1: [REDACTED_BY_SECURITY_GUARD]", sanitized)
        
        # 4. Strip generic high-entropy hexadecimal keys (common in cloud logs)
        sanitized = re.sub(r"\b[a-fA-F0-9]{32,}\b", "[REDACTED_HASH]", sanitized)

        return sanitized.strip()

    @staticmethod
    def is_file_safe(filename: str, file_bytes: bytes) -> bool:
        """
        Verifies document safety by checking extensions and magic bytes signatures
        to prevent executable scripting bypasses.
        """
        allowed_extensions = {'.txt', '.pdf', '.docx'}
        ext = filename.lower()[filename.rfind('.'):] if '.' in filename else ''
        
        if ext not in allowed_extensions:
            return False
            
        if ext == '.pdf' and not file_bytes.startswith(b'%PDF'):
            return False
        if ext == '.docx' and not file_bytes.startswith(b'PK\x03\x04'):
            return False
            
        return True