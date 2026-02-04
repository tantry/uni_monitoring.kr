"""
Formats program data for Telegram alerts using standardized program format
"""
from sources import SOURCE_CONFIG, MUSIC_TYPES

class TelegramFormatter:
    @staticmethod
    def format_alert(programs, alert_type="new_programs"):
        """Format programs for Telegram notification"""
        if not programs:
            return None
        
        if alert_type == "new_programs":
            return TelegramFormatter._format_new_programs(programs)
        else:
            return TelegramFormatter._format_generic(programs)
    
    @staticmethod
    def _format_new_programs(programs):
        """Format new program discoveries"""
        # Group by source
        by_source = {}
        for program in programs:
            source = program.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(program)
        
        # Build message
        total = len(programs)
        message = f"🎵 **New University Music Programs Found** ({total})\n\n"
        
        for source, source_programs in by_source.items():
            source_info = SOURCE_CONFIG.get(source, {})
            message += f"{source_info.get('icon', '📄')} **{source_info.get('name', source.upper())}** ({len(source_programs)})\n"
            
            for program in source_programs:
                message += TelegramFormatter._format_program_line(program)
                message += "\n"
            
            message += "\n"
        
        message += "---\n"
        message += "🔔 Check config for details\n"
        
        return message
    
    @staticmethod
    def _format_program_line(program):
        """Format a single program as a compact line"""
        # Basic info
        uni = program.get('university', 'Unknown')
        music_icons = program.get('music_icons', '🎵')
        deadline = program.get('deadline', 'No deadline')
        days = program.get('deadline_days')
        
        # Build line
        line = f"  • **{uni}** {music_icons}"
        
        # Add department if available
        dept = program.get('department')
        if dept and dept != "음악관련학과":
            line += f" - {dept}"
        
        # Add deadline info
        if days is not None:
            urgency_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(
                program.get('urgency', 'normal'), '⚪'
            )
            line += f" | {urgency_icon} ~{deadline} ({days}d)"
        elif deadline:
            line += f" | ⏰ {deadline}"
        
        # Add location if not obvious from university name
        location = program.get('location')
        if location and location not in uni:
            line += f" | 📍 {location}"
        
        return line
    
    @staticmethod
    def _format_generic(programs):
        """Generic formatting for any program list"""
        message = "🎵 **University Music Programs**\n\n"
        
        for i, program in enumerate(programs, 1):
            message += f"{i}. {TelegramFormatter._format_program_details(program)}\n\n"
        
        return message
    
    @staticmethod
    def _format_program_details(program):
        """Format detailed program information"""
        lines = []
        
        # University and source
        source_info = SOURCE_CONFIG.get(program.get('source', ''), {})
        source_icon = source_info.get('icon', '📄')
        source_name = source_info.get('name', program.get('source', '').upper())
        
        lines.append(f"{source_icon} **{program['university']}** ({source_name})")
        
        # Music types
        music_icons = program.get('music_icons', '🎵')
        music_names = program.get('music_names', 'Music')
        lines.append(f"{music_icons} **{music_names}**")
        
        # Department and program
        dept = program.get('department')
        if dept:
            lines.append(f"🏫 **Department**: {dept}")
        
        prog = program.get('program')
        if prog and len(prog) < 100:
            lines.append(f"📋 **Program**: {prog}")
        
        # Deadline with urgency
        deadline = program.get('deadline')
        if deadline:
            urgency = program.get('urgency', 'normal')
            urgency_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(urgency, '⚪')
            days = program.get('deadline_days')
            
            deadline_line = f"⏰ **Deadline**: {urgency_icon} {deadline}"
            if days is not None:
                deadline_line += f" ({days} days)"
            
            lines.append(deadline_line)
        
        # Location
        location = program.get('location')
        if location:
            lines.append(f"📍 **Location**: {location}")
        
        # URL if available
        url = program.get('url')
        if url and url.startswith('http'):
            domain = url.split('/')[2] if '//' in url else url[:30]
            lines.append(f"🔗 **Link**: {domain}")
        
        return '\n'.join(lines)

# Test function
def test_formatter():
    """Test the formatter"""
    from sources import SOURCE_CONFIG
    
    sample_programs = [
        {
            'source': 'adiga',
            'university': '서울대학교',
            'department': '실용음악학과',
            'program': '재즈보컬 추가모집 (R&B 포함)',
            'deadline': '2026.12.20',
            'deadline_days': 5,
            'url': 'https://example.com',
            'music_types': ['applied_contemporary', 'vocal_specialized'],
            'music_icons': '🎸 🎤',
            'music_names': '실용음악 • 보컬전문',
            'location': '서울',
            'urgency': 'medium',
        }
    ]
    
    print("🧪 Testing Telegram formatter...\n")
    
    formatter = TelegramFormatter()
    message = formatter.format_alert(sample_programs, "new_programs")
    
    print("📱 TELEGRAM FORMAT:")
    print("=" * 50)
    print(message)
    print("=" * 50)

if __name__ == "__main__":
    test_formatter()
