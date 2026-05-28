"""
Skill Taxonomy

Universal skill classification taxonomy with tier1 and tier2 categories.
Reused from MP3 Career Analysis System.
"""
from typing import Dict, List, Tuple, Optional


class SkillTaxonomy:
    """Universal skill taxonomy for classification"""
    
    # Complete taxonomy structure
    TAXONOMY = {
        "Technical": {
            "Programming Languages": [
                "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C", "Go", 
                "Golang", "GoLang", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", 
                "R", "MATLAB", "C++14", "C/C++", "VBA", "Solidity"
            ],
            "Web Frameworks": [
                "React", "React.js", "ReactJS", "Angular", "Vue", "Vue.js", "Svelte",
                "Next.js", "Django", "Flask", "FastAPI", "Spring Boot", "Node.js", 
                "Express.js", "NestJS", "ASP.NET", "ASP.Net", ".NET", ".NET Core",
                "Laravel", "Rails", "Entity Framework", "Hibernate"
            ],
            "AI/ML Frameworks": [
                "TensorFlow", "PyTorch", "Scikit-learn", "scikit-learn", "Keras",
                "MXNet", "HuggingFace Transformers", "OpenCV", "Deep Learning",
                "Machine Learning", "Machine Learning (ML)", "Neural Networks",
                "Deep Neural Networks", "Computer Vision", "NLP", 
                "Natural Language Processing", "Reinforcement Learning"
            ],
            "LLM & Generative AI": [
                "LLMs", "Large Language Models", "Large Language Models (LLMs)",
                "Generative AI", "Gen AI", "LLM Frameworks", "LLM Integration",
                "LLM integration", "LLM post-training", "LangChain", "Langchain",
                "LlamaIndex", "RAG (Retrieval Augmented Generation)", "RAG Architectures",
                "Prompt Engineering", "Prompt engineering", "OpenAI", "Anthropic SDKs",
                "Multimodal AI", "Multimodal Modeling", "Vision-Language Models",
                "Agentic AI", "AI", "Artificial Intelligence", "Artificial Intelligence (AI)",
                "AI Concepts", "AI Development Lifecycle", "AI Prototyping"
            ],
            "Cloud & Infrastructure": [
                "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
                "Ansible", "Jenkins", "CI/CD", "DevOps", "Microservices", "Serverless",
                "Cloud Computing", "Cloud Platforms", "Cloud Service", "Cloud Environments",
                "Cloud Native Technology", "Edge Computing", "Distributed Systems",
                "Distributed architecture", "High-Performance Computing"
            ],
            "Databases & Data Storage": [
                "PostgreSQL", "Postgres", "MySQL", "MongoDB", "Redis", "Elasticsearch",
                "Oracle", "SQL Server", "MS SQL Server", "DynamoDB", "Cassandra", "Neo4j",
                "NoSQL", "noSQL", "Relational Databases", "Vector databases", 
                "Columnar Database", "Snowflake", "BigQuery", "Redshift", "Database",
                "Databases", "Database Design", "Cold Storage", "Storage", "Storage engines"
            ],
            "Data Engineering & ETL": [
                "ETL", "ETL Development", "ETL tools", "Data Pipeline", "Data Pipelines",
                "Data Ingestion", "Apache Spark", "Spark", "PySpark", "Pyspark", 
                "Hadoop", "Hadoop Ecosystem", "Flink", "Kafka", "Airbyte", "Fivetran",
                "Stitch", "dbt", "Hive SQL", "Data Warehousing", "Data Processing"
            ],
            "Data Science & Analytics": [
                "Data Analysis", "Data Analytics", "Data Science", "Data Visualization",
                "Data Visualisation", "Statistical Analysis", "Statistical Modeling",
                "Statistics", "Tableau", "Power BI", "Looker", "Qlik", "Excel",
                "Google Sheets", "Data Studio", "Business Intelligence", "Dashboarding",
                "Dashboard Development", "Dashboard building", "Report Design", 
                "Report Automation", "Reporting", "Data Modeling", "Data Mining",
                "Data Wrangling", "Data Storytelling", "Alteryx", "SAS", "SPSS",
                "NumPy", "Pandas", "Matplotlib", "Seaborn"
            ],
            "API & Integration": [
                "REST", "REST APIs", "RESTful APIs", "REST API design", "GraphQL",
                "gRPC", "API Design", "API Integration", "API Testing", "Postman",
                "Swagger", "Asynchronous Programming", "Asynchronous frameworks"
            ],
            "Mobile Development": [
                "Android Development", "React Native", "Mobile Development",
                "iOS Development", "Swift", "Kotlin"
            ],
            "DevOps & Automation": [
                "CI/CD", "Continuous Deployment", "Docker", "Kubernetes", "Jenkins",
                "Automation", "Shell Scripting", "Scripting", "Linux", "Linux/Unix",
                "Unix", "Windows PowerShell", "Git", "GitHub", "GitLab"
            ],
            "Testing & QA": [
                "Unit Testing", "Integration Testing", "Test Automation", "Automated Testing",
                "UI Testing", "API Testing", "Selenium", "Jest", "Pytest", "JUnit", 
                "GTest Framework", "TDD", "BDD", "Quality Assurance", "Quality Control",
                "Software Quality Assurance", "Debugging", "Troubleshooting", "Code Review"
            ],
            "Security & Blockchain": [
                "Cybersecurity", "Security", "Penetration Testing", "Encryption", "OAuth",
                "JWT", "SSL/TLS", "OWASP", "Security Auditing", "Auth protocols",
                "Blockchain Technology", "Smart Contract Development", "Solidity",
                "Multi-Signature Wallets", "Secure Storage Solutions"
            ],
            "Software Engineering": [
                "Software Engineering", "Software Development", "Software Architecture",
                "Software Design", "Software Design Principles", "Design Patterns",
                "Design Principles", "OOP", "Object-Oriented Programming", 
                "Object Oriented Concepts", "SDLC", "SDLC Waterfall", "Agile methodologies",
                "Agile/Scrum", "Code Generation", "Modular architecture", "MV* Framework",
                "Component Development", "Performance Optimization", "System Performance Optimization",
                "Front-end Performance Optimization", "Performance profiling", 
                "Pipeline Optimizations", "Scalable Platforms"
            ],
            "Computer Science Fundamentals": [
                "Data Structures", "Data Structure and Algorithms", "Data Structures and Algorithms",
                "Algorithms", "Algorithm Development", "Computer Science", "Computer Engineering",
                "Computer Programming", "Computer Systems", "Computer Architecture",
                "Operating Systems", "Networks", "Compiler", "Program Analysis",
                "Multithreading", "Multi-threaded Programming", "Distributed consistency",
                "Mathematics", "Calculus", "Linear Algebra", "Statistics"
            ],
            "Specialized Domains": [
                "Robotics", "ROS", "Autonomous Systems", "Motion Planning", "Behavior Planning",
                "Computer Vision", "CV", "Image Processing", "Image Analysis", "Speech Processing",
                "Recommendation Systems", "Collaborative Filtering", "Matrix Factorization",
                "Factorization Machines", "Gradient Boosting Trees", "Logistic Regression",
                "Word2vec", "Search", "Search Engine", "Multi-modal Matching",
                "Content Curation", "Campaign Management", "Digital Asset Management",
                "Telemetry", "Traffic routing", "Service Stability", "Risk control systems",
                "Account system", "User data systems", "Data access tools"
            ],
            "Web Technologies": [
                "HTML", "HTML5", "CSS", "CSS3", "JavaScript", "JavaScript (ES6+)",
                "TypeScript", "JQuery", "Responsive Design", "Cross-Browser Compatibility",
                "Browser Compatibility", "Browser", "Frontend Development", 
                "User Interface Development", "User Interface (UI) Development",
                "UX/UI Design", "Web Applications", "Web Stack", "Web Automation",
                "Backend Technologies", "Back-end technologies", "Backend Frameworks"
            ],
            "Tools & Platforms": [
                "Git", "GitHub", "GitLab", "Jira", "Confluence", "Slack",
                "VS Code", "IntelliJ", "Postman", "Swagger", "Linux", "Unix",
                "Google Docs", "PowerPoint", "MS Dynamics 365", "Outsystems",
                "Disney+ / Disney+ Hotstar", "Planning Tools"
            ]
        },
        "Business/Ops": {
            "Project Management": [
                "Agile", "Scrum", "Kanban", "Waterfall", "Project Planning",
                "Sprint Planning", "Backlog Management", "Roadmap Planning",
                "Project Management", "Agile methodologies", "Agile/Scrum",
                "Workflow Design"
            ],
            "Business Analysis": [
                "Requirements Gathering", "Business Requirements Gathering", 
                "Stakeholder Management", "Business Process", "Gap Analysis", 
                "User Stories", "Use Cases", "Wireframing", "Business Understanding",
                "Market Insight", "Root Cause Analysis", "Analysis"
            ],
            "Data Analysis": [
                "Excel", "Google Sheets", "Data Modeling", "Statistical Analysis",
                "A/B Testing", "A/B testing evaluation", "Metrics", "KPIs", 
                "KPI Definition", "Reporting", "Data Analysis", "Data Analytics",
                "Data-Driven Decision Making", "Data-driven decision making",
                "Data-driven problem-solving", "Financial Modeling", 
                "Multivariate Experiments", "Model Evaluation", "Model Monitoring",
                "Evaluation Techniques"
            ],
            "Product Management": [
                "Product Strategy", "Product Roadmap", "User Research",
                "Market Analysis", "Feature Prioritization", "Product Launch",
                "Product Ownership"
            ]
        },
        "Soft Skills": {
            "Communication": [
                "Written Communication", "Verbal Communication", "Presentation",
                "Documentation", "Technical Writing", "Public Speaking",
                "Communication", "Communication Skills", "Presentation Skills",
                "Storytelling", "Data Storytelling", "Team Communication",
                "Interpersonal Skills"
            ],
            "Leadership": [
                "Team Leadership", "Mentoring", "Coaching", "People Management",
                "Conflict Resolution", "Decision Making", "Leadership", "Mentorship",
                "Ownership"
            ],
            "Problem Solving": [
                "Critical Thinking", "Analytical Skills", "Troubleshooting",
                "Debugging", "Root Cause Analysis", "Creative Thinking",
                "Problem Solving", "Problem-Solving Skills", "Problem-solving",
                "Problem-solving skills", "Complex Problem-Solving", 
                "Analytical Thinking", "Analytical Mindset", "Analytical skills",
                "Logical Thinking", "Logical Skills", "Rational Thinking",
                "Structured Thinking", "Investigational Thinking", "Critical-thinking",
                "Data-driven problem-solving"
            ],
            "Collaboration": [
                "Teamwork", "Cross-functional Collaboration", "Stakeholder Engagement",
                "Negotiation", "Consensus Building", "Team Collaboration",
                "Cross-functional Teamwork", "Collaborative", "Collaboration"
            ],
            "Adaptability": [
                "Learning Agility", "Flexibility", "Change Management",
                "Resilience", "Growth Mindset", "Adaptability", "Learning",
                "Learning Ability", "Quick Learner", "Independent Learner",
                "Eagerness to Learn", "Curiosity", "Innovation Capability",
                "Creativity"
            ],
            "Work Ethic": [
                "Self-Motivation", "Self-driven", "Proactive", "Attention to Detail",
                "Organization", "Organizational Skills", "Time Management",
                "PC Literacy"
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
        
        # LLM & Generative AI keywords (check first - most specific)
        if any(kw in combined_text for kw in [
            'llm', 'large language model', 'generative ai', 'gen ai', 'langchain',
            'llamaindex', 'rag', 'retrieval augmented', 'prompt engineering',
            'openai', 'anthropic', 'multimodal ai', 'agentic ai', 'vision-language'
        ]):
            return ("Technical", "LLM & Generative AI")
        
        # AI/ML keywords
        if any(kw in combined_text for kw in [
            'tensorflow', 'pytorch', 'keras', 'scikit', 'machine learning', 'ml',
            'deep learning', 'neural network', 'computer vision', 'nlp', 
            'natural language processing', 'reinforcement learning', 'huggingface',
            'opencv', 'mxnet'
        ]):
            return ("Technical", "AI/ML Frameworks")
        
        # Programming language keywords
        if any(kw in combined_text for kw in [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'golang',
            'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'solidity'
        ]) and not any(kw in combined_text for kw in ['framework', 'library', 'react', 'angular', 'django']):
            return ("Technical", "Programming Languages")
        
        # Web framework keywords
        if any(kw in combined_text for kw in [
            'react', 'angular', 'vue', 'svelte', 'next.js', 'django', 'flask',
            'fastapi', 'spring boot', 'node.js', 'express', 'nestjs', 'asp.net',
            '.net core', 'laravel', 'rails'
        ]):
            return ("Technical", "Web Frameworks")
        
        # Cloud keywords
        if any(kw in combined_text for kw in [
            'cloud', 'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
            'devops', 'terraform', 'ansible', 'microservices', 'serverless',
            'edge computing', 'distributed system'
        ]):
            return ("Technical", "Cloud & Infrastructure")
        
        # Database keywords
        if any(kw in combined_text for kw in [
            'database', 'sql', 'nosql', 'postgres', 'mysql', 'mongo', 'redis',
            'elasticsearch', 'oracle', 'snowflake', 'bigquery', 'redshift',
            'vector database', 'columnar'
        ]):
            return ("Technical", "Databases & Data Storage")
        
        # Data Engineering keywords
        if any(kw in combined_text for kw in [
            'etl', 'data pipeline', 'data ingestion', 'spark', 'pyspark', 'hadoop',
            'kafka', 'flink', 'airbyte', 'fivetran', 'dbt', 'data warehousing'
        ]):
            return ("Technical", "Data Engineering & ETL")
        
        # Data Science keywords
        if any(kw in combined_text for kw in [
            'data analysis', 'data science', 'data visualization', 'tableau',
            'power bi', 'looker', 'statistical', 'analytics', 'dashboard',
            'reporting', 'data modeling', 'data mining', 'numpy', 'pandas'
        ]):
            return ("Technical", "Data Science & Analytics")
        
        # API keywords
        if any(kw in combined_text for kw in [
            'rest', 'restful', 'graphql', 'grpc', 'api design', 'api integration',
            'api testing', 'asynchronous'
        ]):
            return ("Technical", "API & Integration")
        
        # Mobile keywords
        if any(kw in combined_text for kw in [
            'android', 'ios', 'mobile', 'react native', 'swift', 'kotlin'
        ]):
            return ("Technical", "Mobile Development")
        
        # Testing keywords
        if any(kw in combined_text for kw in [
            'testing', 'test automation', 'selenium', 'jest', 'pytest', 'junit',
            'quality assurance', 'qa', 'debugging', 'tdd', 'bdd'
        ]):
            return ("Technical", "Testing & QA")
        
        # Security keywords
        if any(kw in combined_text for kw in [
            'security', 'cybersecurity', 'encryption', 'oauth', 'jwt', 'blockchain',
            'smart contract', 'penetration testing', 'auth'
        ]):
            return ("Technical", "Security & Blockchain")
        
        # Software Engineering keywords
        if any(kw in combined_text for kw in [
            'software engineering', 'software development', 'software architecture',
            'design pattern', 'oop', 'object-oriented', 'sdlc', 'agile', 'scrum',
            'code generation', 'modular', 'performance optimization'
        ]):
            return ("Technical", "Software Engineering")
        
        # Computer Science keywords
        if any(kw in combined_text for kw in [
            'data structure', 'algorithm', 'computer science', 'operating system',
            'network', 'compiler', 'multithreading', 'distributed', 'mathematics',
            'calculus', 'linear algebra'
        ]):
            return ("Technical", "Computer Science Fundamentals")
        
        # Web Technologies keywords
        if any(kw in combined_text for kw in [
            'html', 'css', 'frontend', 'ui', 'ux', 'responsive', 'browser',
            'web application', 'jquery', 'backend'
        ]):
            return ("Technical", "Web Technologies")
        
        # Specialized domains
        if any(kw in combined_text for kw in [
            'robotics', 'ros', 'autonomous', 'motion planning', 'recommendation',
            'search engine', 'image processing', 'speech', 'telemetry'
        ]):
            return ("Technical", "Specialized Domains")
        
        # Business keywords
        if any(kw in combined_text for kw in [
            'agile', 'scrum', 'project', 'management', 'planning', 'workflow'
        ]):
            return ("Business/Ops", "Project Management")
        
        if any(kw in combined_text for kw in [
            'business', 'requirements', 'stakeholder', 'analysis', 'market'
        ]):
            return ("Business/Ops", "Business Analysis")
        
        if any(kw in combined_text for kw in [
            'a/b test', 'metrics', 'kpi', 'financial modeling', 'evaluation'
        ]):
            return ("Business/Ops", "Data Analysis")
        
        if any(kw in combined_text for kw in [
            'product', 'roadmap', 'feature prioritization'
        ]):
            return ("Business/Ops", "Product Management")
        
        # Soft skill keywords
        if any(kw in combined_text for kw in [
            'communication', 'presentation', 'writing', 'speaking', 'storytelling'
        ]):
            return ("Soft Skills", "Communication")
        
        if any(kw in combined_text for kw in [
            'leadership', 'mentor', 'coach', 'manage', 'lead', 'ownership'
        ]):
            return ("Soft Skills", "Leadership")
        
        if any(kw in combined_text for kw in [
            'problem', 'solving', 'analytical', 'critical', 'thinking', 'logical',
            'rational', 'structured', 'investigational'
        ]):
            return ("Soft Skills", "Problem Solving")
        
        if any(kw in combined_text for kw in [
            'team', 'collaboration', 'cooperative', 'cross-functional'
        ]):
            return ("Soft Skills", "Collaboration")
        
        if any(kw in combined_text for kw in [
            'learning', 'adaptability', 'flexibility', 'curiosity', 'innovation',
            'creativity', 'quick learner', 'eagerness'
        ]):
            return ("Soft Skills", "Adaptability")
        
        if any(kw in combined_text for kw in [
            'self-motivated', 'proactive', 'attention to detail', 'organization',
            'time management'
        ]):
            return ("Soft Skills", "Work Ethic")
        
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
