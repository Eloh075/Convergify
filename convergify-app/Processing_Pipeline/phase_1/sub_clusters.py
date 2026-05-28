"""
Role Sub-Cluster Definitions
Keyword triggers for classifying jobs into specific sub-clusters
"""

SUB_CLUSTER_DEFINITIONS = {
    "Software Engineer": {
        "Frontend": [
            "React", "Vue", "Angular", "TypeScript", "UI/UX", "DOM", "Webpack",
            "CSS", "HTML", "JavaScript", "Frontend", "Front-end", "User Interface",
            "Responsive Design", "Web Components", "Next.js", "Svelte"
        ],
        "Backend": [
            "Node.js", "Java", "Spring", "Python", "Django", "FastAPI", "Golang",
            "REST APIs", "Microservices", "PostgreSQL", "MySQL", "MongoDB",
            "Backend", "Back-end", "Server", "API Development", "Express.js",
            "Flask", "Ruby on Rails", "GraphQL"
        ],
        "Systems": [
            "C", "C++", "Rust", "Embedded", "Linux Kernel", "Memory Management",
            "Systems Programming", "Operating Systems", "Device Drivers",
            "Assembly", "RTOS", "Firmware", "Hardware", "Low-level"
        ],
        "Generalist": [
            "any programming language", "willingness to learn", "rotational program",
            "general software", "various technologies", "multiple stacks"
        ]
    },
    
    "Data Analyst": {
        "Business Intelligence": [
            "Tableau", "PowerBI", "Power BI", "Looker", "SQL", "ETL",
            "Stakeholder Reporting", "Business Intelligence", "BI", "Data Visualization",
            "Dashboards", "Reporting", "QlikView", "Sisense"
        ],
        "Product Analytics": [
            "Mixpanel", "Amplitude", "A/B Testing", "User Funnels", "Retention Metrics",
            "Product Analytics", "User Behavior", "Cohort Analysis", "Event Tracking",
            "Product Metrics", "User Engagement", "Conversion Funnel"
        ],
        "Marketing/Growth": [
            "Google Analytics", "CAC", "LTV", "Conversion Rate Optimization", "CRO",
            "HubSpot", "Marketing Analytics", "Growth Analytics", "Customer Acquisition",
            "Marketing Metrics", "Campaign Analysis", "Attribution", "SEO Analytics"
        ],
        "Generalist": [
            "any analytics tool", "willingness to learn", "rotational program",
            "general analytics", "various data tools"
        ]
    },
    
    "AI Engineer": {
        "Generative/NLP": [
            "LLMs", "RAG", "LangChain", "Prompt Engineering", "OpenAI API",
            "Hugging Face", "Transformers", "NLP", "Natural Language Processing",
            "GPT", "BERT", "Text Generation", "Chatbots", "Language Models",
            "Generative AI", "LLM", "ChatGPT"
        ],
        "Computer Vision": [
            "OpenCV", "YOLO", "CNNs", "Image Segmentation", "PyTorch Vision",
            "Computer Vision", "Image Processing", "Object Detection",
            "Image Recognition", "Video Analysis", "Convolutional Neural Networks",
            "Image Classification", "Face Recognition", "OCR"
        ],
        "MLOps": [
            "Docker", "Kubernetes", "MLflow", "AWS SageMaker", "TensorRT",
            "CI/CD for ML", "MLOps", "Model Deployment", "ML Infrastructure",
            "Model Serving", "ML Pipeline", "Kubeflow", "Model Monitoring",
            "ML Engineering", "Production ML"
        ],
        "Generalist": [
            "any AI framework", "willingness to learn", "rotational program",
            "general AI", "various ML tools", "machine learning"
        ]
    },
    
    "Full Stack Developer": {
        "JavaScript Ecosystem": [
            "MERN", "MongoDB", "Express", "React", "Node", "Next.js",
            "TypeScript", "Tailwind", "JavaScript", "Full Stack JavaScript",
            "MEAN", "Vue.js", "Nuxt.js", "Nest.js"
        ],
        "Enterprise": [
            "Java Spring Boot", "Angular", "C#", ".NET", "React", "SQL Server",
            "Enterprise", "Spring Framework", "ASP.NET", "Entity Framework",
            "Oracle", "SAP", "Enterprise Applications"
        ],
        "Python/Ruby": [
            "Django", "Flask", "Ruby on Rails", "HTMX", "PostgreSQL",
            "Python Full Stack", "Ruby", "Rails", "Sinatra", "FastAPI",
            "SQLAlchemy", "ActiveRecord"
        ],
        "Generalist": [
            "any stack", "willingness to learn", "rotational program",
            "general full stack", "various technologies", "multiple frameworks"
        ]
    },
    
    "Business Analyst": {
        "IT/Systems": [
            "ERP", "SAP", "Oracle", "CRM", "Salesforce", "SDLC",
            "API Requirements", "UAT", "User Acceptance Testing",
            "Systems Analysis", "Technical Requirements", "IT Systems",
            "Enterprise Systems", "System Integration"
        ],
        "Agile/Scrum": [
            "Jira", "User Stories", "Backlog Grooming", "Sprint Planning",
            "Confluence", "Agile", "Scrum", "Scrum Master", "Product Owner",
            "Agile Methodology", "Sprint", "Kanban", "Agile BA"
        ],
        "Strategy/Operations": [
            "Process Mapping", "BPMN", "Financial Modeling", "Cost-Benefit Analysis",
            "Lean", "Six Sigma", "Business Strategy", "Operations",
            "Process Improvement", "Business Process", "Operational Excellence",
            "Strategic Planning", "ROI Analysis"
        ],
        "Generalist": [
            "any BA tool", "willingness to learn", "rotational program",
            "general business analysis", "various domains"
        ]
    },
    
    "Product Manager": {
        "Technical": [
            "System Architecture", "API Design", "Cloud Infrastructure",
            "Developer Experience", "DX", "Technical Product Manager", "TPM",
            "Platform", "Infrastructure", "Technical PM", "API Product",
            "Developer Tools", "Technical Strategy"
        ],
        "Growth": [
            "PLG", "Product-Led Growth", "A/B Testing", "Activation Rate",
            "Pricing Strategy", "Growth PM", "User Acquisition", "Monetization",
            "Growth Metrics", "Conversion Optimization", "Retention",
            "Growth Strategy", "User Onboarding"
        ],
        "Core/Feature": [
            "User Research", "Wireframing", "Figma", "PRDs",
            "Product Requirement Docs", "Go-to-Market", "GTM",
            "Product Strategy", "User Experience", "Feature Development",
            "Product Roadmap", "User Journey", "Product Design"
        ],
        "Generalist": [
            "any product area", "willingness to learn", "rotational program",
            "general product management", "various products"
        ]
    }
}


def get_all_sub_clusters() -> list[str]:
    """Get list of all sub-cluster names"""
    clusters = []
    for role_clusters in SUB_CLUSTER_DEFINITIONS.values():
        clusters.extend(role_clusters.keys())
    return clusters


def get_sub_cluster_for_role(role: str) -> list[str]:
    """Get sub-clusters for a specific role"""
    return list(SUB_CLUSTER_DEFINITIONS.get(role, {}).keys())
