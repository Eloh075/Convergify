"""
Skill Taxonomy

Universal skill classification taxonomy with tier1 and tier2 categories.
"""
from typing import Dict, List, Tuple, Optional


class SkillTaxonomy:
    """Universal skill taxonomy for classification"""
    
    # Complete taxonomy structure
    TAXONOMY = {
        "Technical": {
            "Programming Languages": [
                "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", 
                "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB"
            ],
            "Frameworks & Libraries": [
                "React", "Angular", "Vue.js", "Django", "Flask", "FastAPI", 
                "Spring Boot", "Node.js", "Express.js", "TensorFlow", "PyTorch",
                "Scikit-learn", "Pandas", "NumPy", ".NET", "Laravel", "Rails"
            ],
            "Cloud & Infrastructure": [
                "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
                "Ansible", "Jenkins", "CI/CD", "DevOps", "Microservices", "Serverless"
            ],
            "Databases": [
                "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
                "Oracle", "SQL Server", "DynamoDB", "Cassandra", "Neo4j"
            ],
            "Tools & Platforms": [
                "Git", "GitHub", "GitLab", "Jira", "Confluence", "Slack",
                "VS Code", "IntelliJ", "Postman", "Swagger", "Linux", "Unix"
            ],
            "Data & Analytics": [
                "SQL", "Data Analysis", "Data Visualization", "ETL", "Big Data",
                "Hadoop", "Spark", "Tableau", "Power BI", "Looker"
            ],
            "Security": [
                "Cybersecurity", "Penetration Testing", "Encryption", "OAuth",
                "JWT", "SSL/TLS", "OWASP", "Security Auditing"
            ],
            "Testing": [
                "Unit Testing", "Integration Testing", "Test Automation",
                "Selenium", "Jest", "Pytest", "JUnit", "TDD", "BDD"
            ]
        },
        "Business/Ops": {
            "Project Management": [
                "Agile", "Scrum", "Kanban", "Waterfall", "Project Planning",
                "Sprint Planning", "Backlog Management", "Roadmap Planning"
            ],
            "Business Analysis": [
                "Requirements Gathering", "Stakeholder Management", "Business Process",
                "Gap Analysis", "User Stories", "Use Cases", "Wireframing"
            ],
            "Data Analysis": [
                "Excel", "Google Sheets", "Data Modeling", "Statistical Analysis",
                "A/B Testing", "Metrics", "KPIs", "Reporting"
            ],
            "Product Management": [
                "Product Strategy", "Product Roadmap", "User Research",
                "Market Analysis", "Feature Prioritization", "Product Launch"
            ]
        },
        "Soft Skills": {
            "Communication": [
                "Written Communication", "Verbal Communication", "Presentation",
                "Documentation", "Technical Writing", "Public Speaking"
            ],
            "Leadership": [
                "Team Leadership", "Mentoring", "Coaching", "People Management",
                "Conflict Resolution", "Decision Making"
            ],
            "Problem Solving": [
                "Critical Thinking", "Analytical Skills", "Troubleshooting",
                "Debugging", "Root Cause Analysis", "Creative Thinking"
            ],
            "Collaboration": [
                "Teamwork", "Cross-functional Collaboration", "Stakeholder Engagement",
                "Negotiation", "Consensus Building"
            ],
            "Adaptability": [
                "Learning Agility", "Flexibility", "Change Management",
                "Resilience", "Growth Mindset"
            ]
        }
    }
    
    def __init__(self):
        """Initialize taxonomy with reverse lookup maps"""
        self._build_lookup_maps()
    
    def _build_lookup_maps(self):
        """Build reverse lookup maps for fast classification"""
        self.skill_to_category = {}
        
        for tier1, tier2_dict in self.TAXONOMY.items():
            for tier2, skills in tier2_dict.items():
                for skill in skills:
                    # Store lowercase for case-insensitive matching
                    self.skill_to_category[skill.lower()] = (tier1, tier2)
    
    def classify_skill(
        self, 
        skill_name: str, 
        context: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Classify skill into tier1 and tier2 categories
        
        Args:
            skill_name: Name of the skill
            context: Optional context for better classification
            
        Returns:
            Tuple of (tier1, tier2) categories
        """
        # Try exact match first (case-insensitive)
        skill_lower = skill_name.lower()
        if skill_lower in self.skill_to_category:
            return self.skill_to_category[skill_lower]
        
        # Try partial match
        for known_skill, (tier1, tier2) in self.skill_to_category.items():
            if known_skill in skill_lower or skill_lower in known_skill:
                return (tier1, tier2)
        
        # Default classification based on keywords
        return self._classify_by_keywords(skill_name, context)
    
    def _classify_by_keywords(
        self, 
        skill_name: str, 
        context: Optional[str] = None
    ) -> Tuple[str, str]:
        """Classify skill using keyword matching"""
        skill_lower = skill_name.lower()
        combined_text = f"{skill_lower} {context or ''}".lower()
        
        # Technical keywords
        if any(kw in combined_text for kw in [
            'programming', 'code', 'coding', 'development', 'developer',
            'language', 'framework', 'library', 'api'
        ]):
            if any(kw in combined_text for kw in ['python', 'java', 'javascript', 'c++', 'ruby']):
                return ("Technical", "Programming Languages")
            elif any(kw in combined_text for kw in ['react', 'angular', 'django', 'spring']):
                return ("Technical", "Frameworks & Libraries")
            else:
                return ("Technical", "Tools & Platforms")
        
        # Cloud keywords
        if any(kw in combined_text for kw in [
            'cloud', 'aws', 'azure', 'docker', 'kubernetes', 'devops'
        ]):
            return ("Technical", "Cloud & Infrastructure")
        
        # Database keywords
        if any(kw in combined_text for kw in [
            'database', 'sql', 'nosql', 'postgres', 'mongo', 'redis'
        ]):
            return ("Technical", "Databases")
        
        # Data keywords
        if any(kw in combined_text for kw in [
            'data', 'analytics', 'visualization', 'etl', 'big data'
        ]):
            return ("Technical", "Data & Analytics")
        
        # Business keywords
        if any(kw in combined_text for kw in [
            'agile', 'scrum', 'project', 'management', 'planning'
        ]):
            return ("Business/Ops", "Project Management")
        
        if any(kw in combined_text for kw in [
            'business', 'requirements', 'stakeholder', 'analysis'
        ]):
            return ("Business/Ops", "Business Analysis")
        
        # Soft skill keywords
        if any(kw in combined_text for kw in [
            'communication', 'presentation', 'writing', 'speaking'
        ]):
            return ("Soft Skills", "Communication")
        
        if any(kw in combined_text for kw in [
            'leadership', 'mentor', 'coach', 'manage', 'lead'
        ]):
            return ("Soft Skills", "Leadership")
        
        if any(kw in combined_text for kw in [
            'problem', 'solving', 'analytical', 'critical', 'thinking'
        ]):
            return ("Soft Skills", "Problem Solving")
        
        if any(kw in combined_text for kw in [
            'team', 'collaboration', 'cooperative', 'cross-functional'
        ]):
            return ("Soft Skills", "Collaboration")
        
        # Default to Technical/Tools if no match
        return ("Technical", "Tools & Platforms")
    
    def get_all_tier1_categories(self) -> List[str]:
        """Get all tier1 categories"""
        return list(self.TAXONOMY.keys())
    
    def get_tier2_categories(self, tier1: str) -> List[str]:
        """Get all tier2 categories for a tier1"""
        return list(self.TAXONOMY.get(tier1, {}).keys())
    
    def is_valid_classification(self, tier1: str, tier2: str) -> bool:
        """Check if tier1/tier2 combination is valid"""
        return tier1 in self.TAXONOMY and tier2 in self.TAXONOMY[tier1]
