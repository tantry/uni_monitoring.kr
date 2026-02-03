cat > CONVERSATION_LIMITS.md << 'EOF'
# CONVERSATION LIMIT HANDLING GUIDE

## 📝 PROBLEM
Claude (and other AI assistants) have conversation length limits. When the conversation gets too long:
- Context gets lost
- Files may not be properly referenced
- Code continuity breaks
- Need to start fresh chats

## 🚨 SYMPTOMS OF LIMIT REACHED
1. "I can't see that file" or "File not in context"
2. Losing track of recent changes
3. Repeating information already discussed
4. Assistant asks for files already provided
5. Code suggestions don't match current state

## 🔧 SOLUTION STRATEGY

### A. PREVENTION (Before hitting limits)
1. **Summarize frequently**: Every 10-15 messages, create a summary
2. **Use GitHub/Gists**: Store code externally and reference links
3. **Create checkpoints**: Save complete state to files
4. **Modular discussions**: One topic per conversation thread

### B. RECOVERY (After hitting limits)
1. **Start new chat** with summary
2. **Reference GitHub repo** for code
3. **Upload key files** again
4. **Provide status summary**

## 📁 PROJECT-SPECIFIC PROTOCOL

### For University Monitoring Project:

#### 1. REGULAR CHECKPOINTS
```bash
# Create checkpoint script
cd ~/uni_monitoring
./create_checkpoint.sh