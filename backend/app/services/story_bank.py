from typing import Dict, List, Optional
from datetime import datetime


class StoryBankService:
    """STAR+Reflection story bank for interview preparation"""

    def __init__(self):
        self.stories = []

    def add_story(
        self,
        user_id: str,
        story: Dict
    ) -> str:
        """Add a new STAR+R story to the bank"""
        
        story_id = f"story_{datetime.now().timestamp()}"
        
        new_story = {
            "id": story_id,
            "user_id": user_id,
            "situation": story.get("situation", ""),
            "task": story.get("task", ""),
            "action": story.get("action", ""),
            "result": story.get("result", ""),
            "reflection": story.get("reflection", ""),
            "tags": story.get("tags", []),
            " archetypes": story.get("archetypes", []),
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.stories.append(new_story)
        
        return story_id

    def get_stories_for_archetype(
        self,
        user_id: str,
        archetype: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get stories that fit a specific archetype"""
        
        user_stories = [s for s in self.stories if s["user_id"] == user_id]
        
        # Sort by archetype match
        scored = []
        for story in user_stories:
            score = 0
            if archetype in story.get("archetypes", []):
                score += 2
            score += len(set(story.get("tags", [])) & set(self.get_archetype_tags(archetype)))
            scored.append((score, story))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        
        return [s[1] for s in scored[:limit]]

    def get_stories_for_questions(
        self,
        user_id: str,
        questions: List[str]
    ) -> List[Dict]:
        """Get stories that can answer specific questions"""
        
        user_stories = [s for s in self.stories if s["user_id"] == user_id]
        
        # Score stories based on question relevance
        scored = []
        for story in user_stories:
            score = 0
            story_text = f"{story['situation']} {story['task']} {story['action']} {story['result']}"
            
            for question in questions:
                question_lower = question.lower()
                # Check for keyword overlap
                keywords = self.extract_keywords(question)
                for kw in keywords:
                    if kw.lower() in story_text.lower():
                        score += 1
            
            scored.append((score, story))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        
        return [s[1] for s in scored[:5]]

    def get_master_stories(self, user_id: str) -> List[Dict]:
        """Get the 5-10 master stories that can answer most questions"""
        
        user_stories = [s for s in self.stories if s["user_id"] == user_id]
        
        # Return up to 10 stories
        return user_stories[:10] if len(user_stories) >= 10 else user_stories

    def format_star_response(self, story: Dict) -> str:
        """Format story as STAR response"""
        
        return f"""**Situation:** {story.get('situation', '')}

**Task:** {story.get('task', '')}

**Action:** {story.get('action', '')}

**Result:** {story.get('result', '')}

**Reflection:** {story.get('reflection', '')}"""

    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for matching"""
        
        # Common interview question keywords
        keywords = []
        
        keyword_map = {
            "lead": ["lead", "team", "manage", "mentor"],
            "conflict": ["conflict", "disagree", "dispute", "tension"],
            "failure": ["fail", "mistake", "wrong", "learn"],
            "success": ["success", "achieve", "accomplish", "deliver"],
            "challenge": ["challenge", "difficult", "hard", "obstacle"],
            "initiative": ["initiative", "proactive", "started", "created"],
            "problem": ["problem", "solve", "fix", "resolve"],
            "decision": ["decision", "choose", "decide", "prioritize"],
            "pressure": ["pressure", "deadline", "stress", "urgent"],
            "conflict": ["conflict", "disagree", "different"]
        }
        
        text_lower = text.lower()
        
        for category, words in keyword_map.items():
            for word in words:
                if word in text_lower:
                    keywords.append(word)
        
        return list(set(keywords))

    def get_archetype_tags(self, archetype: str) -> List[str]:
        """Get relevant tags for an archetype"""
        
        archetype_tags = {
            "fde": ["delivery", "client", "integration", "fast-paced", "customer-facing"],
            "sa": ["architecture", "design", "consulting", "technical", "stakeholder"],
            "pm": ["product", "metrics", "roadmap", "discovery", "strategy"],
            "llmops": ["production", "monitoring", "pipeline", "scale", "reliability"],
            "agentic": ["automation", "agent", "workflow", "autonomous", "error-handling"],
            "transformation": ["change", "adoption", "scaling", "stakeholder", "process"]
        }
        
        return archetype_tags.get(archetype, [])

    def generate_story_prompt(self, archetype: str) -> str:
        """Generate a story prompt for a specific archetype"""
        
        prompts = {
            "fde": """Think of a time when you had to quickly learn a new technology or framework to deliver a customer project. How did you approach it? What was the outcome?""",
            
            "sa": """Describe a time when you had to design a technical solution with incomplete information or competing requirements. How did you make decisions?""",
            
            "pm": """Tell me about a time when you had to prioritize features or projects with limited resources. How did you make your decision?""",
            
            "llmops": """Describe a time when you had to debug a production issue with an ML model or pipeline. What was the problem and how did you solve it?""",
            
            "agentic": """Tell me about a time when you built or automated a process that replaced manual work. What was the impact?""",
            
            "transformation": """Describe a time when you had to get buy-in from stakeholders for a new process or technology. How did you approach it?"""
        }
        
        return prompts.get(archetype, "Tell me about a challenging project you worked on.")

    def export_stories(self, user_id: str) -> str:
        """Export all stories as markdown for the story bank"""
        
        user_stories = [s for s in self.stories if s["user_id"] == user_id]
        
        if not user_stories:
            return "# Story Bank\n\nNo stories yet. Start adding your STAR stories!"
        
        md = "# Story Bank\n\n"
        md += f"Total stories: {len(user_stories)}\n\n"
        
        for i, story in enumerate(user_stories, 1):
            md += f"## Story {i}: {story.get('tags', ['Untagged'])[0]}\n\n"
            md += f"**Tags:** {', '.join(story.get('tags', []))}\n"
            md += f"**Archetypes:** {', '.join(story.get('archetypes', []))}\n\n"
            md += self.format_star_response(story)
            md += "\n\n---\n\n"
        
        return md


# Singleton instance
story_bank = StoryBankService()