import json
from .models import LearningPath, Module, Progress, Recommendation, ProjectSuggestion, Skill, StudentProfile, Badge, StudentBadge

# Curated catalog of Career Goals and their curriculum databases
# We define curriculum blocks for each path.
# Based on the target duration (4, 6, or 8 weeks), we select and condense or expand these blocks.
CURRICULUM_CATALOG = {
    'Full Stack Developer': {
        'skills': ['HTML', 'CSS', 'JavaScript', 'Git', 'SQL', 'Django', 'React', 'APIs'],
        'weeks_data': [
            {
                'title': 'Frontend Foundations (HTML5 & CSS3)',
                'description': 'Master the building blocks of the web. Learn semantic HTML, responsive styling, Flexbox, Grid, and design frameworks.',
                'tags': ['HTML', 'CSS'],
                'resources': {
                    'Video': [
                        {'title': 'HTML & CSS Full Course for Beginners', 'url': 'https://www.youtube.com/watch?v=mU6an7qYJ-Y', 'desc': 'A comprehensive 6-hour video course covering modern web styling.'},
                        {'title': 'Flexbox & CSS Grid Crash Course', 'url': 'https://www.youtube.com/watch?v=T-2HecD48d0', 'desc': 'Visual tutorials on modern CSS layouts.'}
                    ],
                    'Reading': [
                        {'title': 'MDN Web Docs: HTML Basics', 'url': 'https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics', 'desc': 'Official developer guides for HTML structure.'},
                        {'title': 'A Complete Guide to Flexbox', 'url': 'https://css-tricks.com/snippets/css/a-guide-to-flexbox/', 'desc': 'CSS-Tricks reference guide to flex layouts.'}
                    ],
                    'Practice': [
                        {'title': 'freeCodeCamp Responsive Web Design', 'url': 'https://www.freecodecamp.org/learn/responsive-web-design/', 'desc': 'Interactive frontend coding challenges.'},
                        {'title': 'CSS Diner - Learn Selectors', 'url': 'https://flukeout.github.io/', 'desc': 'Fun interactive game to master CSS selector syntax.'}
                    ]
                }
            },
            {
                'title': 'JavaScript Fundamentals & DOM Manipulation',
                'description': 'Add interactivity to your webpages. Learn variables, functions, control flows, arrays, objects, and event handling.',
                'tags': ['JavaScript'],
                'resources': {
                    'Video': [
                        {'title': 'JavaScript Tutorial for Beginners', 'url': 'https://www.youtube.com/watch?v=W6NZfCO5SIk', 'desc': 'Learn JS essentials step-by-step.'},
                        {'title': 'Vanilla JS DOM Manipulation', 'url': 'https://www.youtube.com/watch?v=y17RuWkWdn8', 'desc': 'How to dynamically edit page content using JS.'}
                    ],
                    'Reading': [
                        {'title': 'Modern JavaScript Info', 'url': 'https://javascript.info/', 'desc': 'Clear, comprehensive explanation of JS from basics to advanced.'},
                        {'title': 'Eloquent JavaScript Book', 'url': 'https://eloquentjavascript.net/', 'desc': 'A free digital book on JavaScript coding practices.'}
                    ],
                    'Practice': [
                        {'title': 'JavaScript 30 Day Challenge', 'url': 'https://javascript30.com/', 'desc': '30 vanilla JS projects in 30 days.'},
                        {'title': 'Codewars JS Challenges', 'url': 'https://www.codewars.com/', 'desc': 'Train on small algorithmic coding katas.'}
                    ]
                }
            },
            {
                'title': 'Version Control, Git & Github',
                'description': 'Learn how developers collaborate and track code history. Master commits, branches, pull requests, and hosting code.',
                'tags': ['Git'],
                'resources': {
                    'Video': [
                        {'title': 'Git and GitHub for Beginners', 'url': 'https://www.youtube.com/watch?v=RGOj5yH7evk', 'desc': 'Complete guide to repository management and collaboration.'}
                    ],
                    'Reading': [
                        {'title': 'GitHub Git Cheat Sheet', 'url': 'https://github.com/training-kit/downloads/github-git-cheat-sheet.pdf', 'desc': 'Quick commands reference card.'},
                        {'title': 'Pro Git Book', 'url': 'https://git-scm.com/book/en/v2', 'desc': 'The official guide to Git architecture and advanced features.'}
                    ],
                    'Practice': [
                        {'title': 'Learn Git Branching', 'url': 'https://learngitbranching.js.org/', 'desc': 'Interactive visual simulator for branch manipulations.'}
                    ]
                }
            },
            {
                'title': 'Backend Foundations with Python & Django',
                'description': 'Introduce server-side logic. Set up Django models, views, routing, context variables, and Django template syntax.',
                'tags': ['Python', 'Django'],
                'resources': {
                    'Video': [
                        {'title': 'Django for Beginners Full Course', 'url': 'https://www.youtube.com/watch?v=F5mRW0q-A0o', 'desc': 'Step-by-step introduction to building Django apps.'}
                    ],
                    'Reading': [
                        {'title': 'Writing Your First Django App', 'url': 'https://docs.djangoproject.com/en/stable/intro/tutorial01/', 'desc': 'Official Django framework starter tutorial.'}
                    ],
                    'Practice': [
                        {'title': 'Django Girls Tutorial', 'url': 'https://tutorial.djangogirls.org/', 'desc': 'Building your first blog application from scratch.'}
                    ]
                }
            },
            {
                'title': 'Databases, Models & REST APIs',
                'description': 'Connect your server to SQLite or PostgreSQL database. Design schemas, write Django ORM queries, and build endpoints using Django REST Framework.',
                'tags': ['SQL', 'APIs'],
                'resources': {
                    'Video': [
                        {'title': 'SQL Tutorial - Full Database Course', 'url': 'https://www.youtube.com/watch?v=HXV3zeQKqGY', 'desc': 'Learn schema definitions and relational query syntax.'},
                        {'title': 'Django REST Framework Crash Course', 'url': 'https://www.youtube.com/watch?v=c708Nf0cHrs', 'desc': 'Building JSON APIs for frontend consumers.'}
                    ],
                    'Reading': [
                        {'title': 'Django Models and Databases Guide', 'url': 'https://docs.djangoproject.com/en/stable/topics/db/models/', 'desc': 'Official docs on object-relational mapping.'},
                        {'title': 'Django REST Framework Tutorial', 'url': 'https://www.django-rest-framework.org/tutorial/quickstart/', 'desc': 'Official guide to serializers, viewsets, and routing.'}
                    ],
                    'Practice': [
                        {'title': 'SQLBolt - Interactive SQL Lessons', 'url': 'https://sqlbolt.com/', 'desc': 'Run SQL queries inside your browser to learn query structure.'}
                    ]
                }
            },
            {
                'title': 'Frontend Frameworks: React Basics',
                'description': 'Transition from static files to modern components. Master props, state, functional components, hooks, and fetching API data.',
                'tags': ['React'],
                'resources': {
                    'Video': [
                        {'title': 'React JS Course for Beginners', 'url': 'https://www.youtube.com/watch?v=bMknfKXIFA8', 'desc': 'Learn components, state, and rendering in React.'}
                    ],
                    'Reading': [
                        {'title': 'React Dev Documentation', 'url': 'https://react.dev/learn', 'desc': 'Modern guides and tutorials from the React core team.'}
                    ],
                    'Practice': [
                        {'title': 'Scrimba React Course', 'url': 'https://scrimba.com/learn/learnreact', 'desc': 'Interactive screencast where you can edit code inside the tutorial.'}
                    ]
                }
            },
            {
                'title': 'Advanced Full Stack Integration',
                'description': 'Connect your React frontend with Django backend. Implement CORS, handle JSON token authentication (JWT), and structure request workflows.',
                'tags': ['Django', 'React', 'APIs'],
                'resources': {
                    'Video': [
                        {'title': 'Django + React Full-Stack App Tutorial', 'url': 'https://www.youtube.com/watch?v=c-YsXKIJnWw', 'desc': 'Complete end-to-end integration walkthrough.'}
                    ],
                    'Reading': [
                        {'title': 'How to integrate Django and React', 'url': 'https://www.django-rest-framework.org/', 'desc': 'Articles on API decoupling and CORS configs.'}
                    ],
                    'Practice': [
                        {'title': 'Build a CRUD App with React and Django', 'url': 'https://github.com/', 'desc': 'Github starter templates for testing full stack connections.'}
                    ]
                }
            },
            {
                'title': 'Production Deployment & Cloud Hosting',
                'description': 'Bring your site to the real world. Configure settings.py for security, set up environment files, deploy databases, and host on Render/Vercel.',
                'tags': ['Git'],
                'resources': {
                    'Video': [
                        {'title': 'Deploy Django to Render for Free', 'url': 'https://www.youtube.com/watch?v=H7Z8n5wJ49k', 'desc': 'Visual guide to cloud setups.'}
                    ],
                    'Reading': [
                        {'title': 'Django Deployment Checklist', 'url': 'https://docs.djangoproject.com/en/stable/howto/deployment/checklist/', 'desc': 'Security settings verify list.'}
                    ],
                    'Practice': [
                        {'title': 'Vercel / Render CLI Deployments', 'url': 'https://render.com/docs/deploy-django', 'desc': 'Command line configurations.'}
                    ]
                }
            }
        ],
        'projects': [
            {
                'title': 'Personal Portfolio with Contact Form',
                'difficulty': 'Beginner',
                'description': 'Build a responsive personal website presenting your profile, projects, and a fully functional dynamic contact form.',
                'technologies': 'HTML5, CSS3, JavaScript, GitHub Pages',
                'milestones': '- Design visual mockup (dark/glass style)\n- Write semantic HTML structure\n- Style layout with CSS Flexbox & animations\n- Implement validation on form input via JS\n- Publish to GitHub Pages'
            },
            {
                'title': 'Collaborative Task Management Board',
                'difficulty': 'Intermediate',
                'description': 'An interactive Kanban board app where users can manage project tasks, drag/drop cards across lanes, and categorize issues.',
                'technologies': 'Python, Django, SQLite, HTML5, Vanilla JS',
                'milestones': '- Define database tables for Tasks, Category, and Status\n- Build Django templates & CSS styling\n- Implement AJAX endpoints to edit statuses asynchronously\n- Set up user login restrictions'
            },
            {
                'title': 'SaaS Dashboard with JWT Auth & Data Analytics',
                'difficulty': 'Advanced',
                'description': 'A full-scale React interface calling a Django REST API. Includes token login, search dashboards, data filters, and responsive charts.',
                'technologies': 'React.js, Django REST Framework, SQLite, Charts.js',
                'milestones': '- Scaffold DRF backend with custom serializers\n- Configure JWT Authentication\n- Build React pages with router routes\n- Link charts to database analytics API\n- Host database and web app to cloud servers'
            }
        ]
    },
    'Frontend Developer': {
        'skills': ['HTML', 'CSS', 'JavaScript', 'Git', 'React'],
        'weeks_data': [], # Will populate dynamically if empty or map from Full Stack
        'projects': []
    },
    'Backend Developer': {
        'skills': ['Python', 'SQL', 'Django', 'Git', 'APIs'],
        'weeks_data': [],
        'projects': []
    },
    'Data Scientist': {
        'skills': ['Python', 'SQL', 'Pandas', 'Machine Learning'],
        'weeks_data': [],
        'projects': []
    },
    'Machine Learning Engineer': {
        'skills': ['Python', 'Machine Learning', 'Docker'],
        'weeks_data': [],
        'projects': []
    },
    'Mobile App Developer': {
        'skills': ['JavaScript', 'Git', 'Flutter'],
        'weeks_data': [],
        'projects': []
    },
    'DevOps Engineer': {
        'skills': ['Linux', 'Git', 'Docker'],
        'weeks_data': [],
        'projects': []
    },
    'Cybersecurity Specialist': {
        'skills': ['Linux', 'Git', 'Cryptography'],
        'weeks_data': [],
        'projects': []
    }
}

# Mirror or map similar items to fill up the database logic.
# Let's populate the missing weeks dynamically to ensure high-quality content for ALL options!
# We'll map their curriculums appropriately.

def setup_curriculums():
    # If weeks_data is empty, we set up detailed ones.
    # Frontend Developer
    if not CURRICULUM_CATALOG['Frontend Developer']['weeks_data']:
        CURRICULUM_CATALOG['Frontend Developer']['weeks_data'] = [
            CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][0], # HTML/CSS
            CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][1], # JS
            CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][2], # Git
            {
                'title': 'Advanced Modern CSS & Responsive Layouts',
                'description': 'Master SASS/SCSS, responsive design with Media Queries, fluid typographies, and modern utility-based or container queries.',
                'tags': ['CSS'],
                'resources': {
                    'Video': [{'title': 'Advanced CSS Tutorial', 'url': 'https://www.youtube.com/watch?v=1PnVor3GP_4', 'desc': 'Learn CSS animations, variables, and layouts.'}],
                    'Reading': [{'title': 'A Complete Guide to CSS Grid', 'url': 'https://css-tricks.com/snippets/css/complete-guide-grid/', 'desc': 'Interactive grid layouts reference.'}],
                    'Practice': [{'title': 'CSS Grid Garden', 'url': 'https://cssgridgarden.com/', 'desc': 'Interactive farming game to practice CSS Grid.'}]
                }
            },
            {
                'title': 'Asynchronous Javascript & Web APIs',
                'description': 'Understand Promises, async/await, fetch API, and JSON handling. Manipulate browser storage (Local/Session Storage).',
                'tags': ['JavaScript', 'APIs'],
                'resources': {
                    'Video': [{'title': 'Asynchronous JavaScript Explained', 'url': 'https://www.youtube.com/watch?v=exBgWAIeIeg', 'desc': 'Deep dive into event loop and callbacks.'}],
                    'Reading': [{'title': 'Working with APIs in JS', 'url': 'https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Client-side_web_APIs/Introduction', 'desc': 'MDN introduction to Client-side web APIs.'}]
                }
            },
            CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][5], # React Basics
            {
                'title': 'State Management in React (Redux / Context)',
                'description': 'Learn to manage global application states. Explore React Context API and Redux Toolkit for complex workflows.',
                'tags': ['React'],
                'resources': {
                    'Video': [{'title': 'React Context API vs Redux', 'url': 'https://www.youtube.com/watch?v=5yEG6GhoJBs', 'desc': 'Comparative video tutorial.'}],
                    'Reading': [{'title': 'Redux Toolkit Quick Start', 'url': 'https://redux-toolkit.js.org/introduction/quick-start', 'desc': 'Official quickstart guide.'}]
                }
            },
            CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][7] # Deploy
        ]
        CURRICULUM_CATALOG['Frontend Developer']['projects'] = [
            CURRICULUM_CATALOG['Full Stack Developer']['projects'][0], # Portfolio
            {
                'title': 'Weather Forecast Dashboard',
                'difficulty': 'Intermediate',
                'description': 'Create an interactive app that calls a public Weather API to show weather updates, search history, and temperature conversions.',
                'technologies': 'JavaScript, CSS3, OpenWeather API, LocalStorage',
                'milestones': '- Connect to public weather endpoints\n- Render search histories using local storage\n- Implement smooth CSS loader icons\n- Style background dynamically based on weather conditions'
            },
            {
                'title': 'SaaS Dashboard Workspace UI',
                'difficulty': 'Advanced',
                'description': 'Design a complex Single Page Application (SPA) dashboard featuring grid cards, dark mode toggling, interactive lists, and charts.',
                'technologies': 'React.js, CSS Modules, Chart.js, Vercel',
                'milestones': '- Setup React project with modular styles\n- Implement local state dark-mode toggle\n- Embed interactive Charts\n- Host live site on Vercel'
            }
        ]

    # Backend Developer
    if not CURRICULUM_CATALOG['Backend Developer']['weeks_data']:
        CURRICULUM_CATALOG['Backend Developer']['weeks_data'] = [
            {
                'title': 'Advanced Python Programming & Core Logics',
                'description': 'Learn advanced object-oriented programming (OOP), decorators, file operations, error exceptions, and environment setup.',
                'tags': ['Python'],
                'resources': {
                    'Video': [{'title': 'Python OOP Tutorial', 'url': 'https://www.youtube.com/watch?v=JeznW_7DlB0', 'desc': 'Classes, inheritance, and instances.'}],
                    'Reading': [{'title': 'Real Python: OOP in Python', 'url': 'https://realpython.com/python3-object-oriented-programming/', 'desc': 'Interactive guide to Python classes.'}]
                }
            },
            {
                'title': 'Relational Databases & SQL Queries',
                'description': 'Learn SQL query writing, CRUD commands, joins, relationships, index optimizations, and database design systems.',
                'tags': ['SQL'],
                'resources': {
                    'Video': [{'title': 'SQL Join Statements Visualized', 'url': 'https://www.youtube.com/watch?v=9yeOJ0xxSOY', 'desc': 'Clear animations explaining left/right/inner joins.'}],
                    'Reading': [{'title': 'W3Schools SQL Tutorial', 'url': 'https://www.w3schools.com/sql/', 'desc': 'A standard guide to query syntaxes.'}]
                }
            },
            CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][2], # Git
            CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][3], # Django Basics
            CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][4], # Databases & DRF API
            {
                'title': 'Authentication & Server Authorization',
                'description': 'Implement security systems. Learn Session authentication, Token-based JWT authorization, password hashing, and user permissions.',
                'tags': ['Django'],
                'resources': {
                    'Video': [{'title': 'JWT Authentication in Django', 'url': 'https://www.youtube.com/watch?v=e-R0HS_XRm0', 'desc': 'Set up SimpleJWT in Django REST Framework.'}]
                }
            },
            {
                'title': 'Caching, Task Queues & Optimization',
                'description': 'Optimize backend speeds. Setup Redis caching, background task queues with Celery, and query optimization tools.',
                'tags': ['Django', 'SQL'],
                'resources': {
                    'Video': [{'title': 'Django Caching with Redis', 'url': 'https://www.youtube.com/watch?v=78Vw-9f2Kms', 'desc': 'Introduction to caching.'}]
                }
            },
            {
                'title': 'Deployment, Docker & Containerization',
                'description': 'Package your backend code. Create Dockerfiles, docker-compose setups, configure WSGI servers (Gunicorn), and deploy to cloud VMs.',
                'tags': ['Docker'],
                'resources': {
                    'Video': [{'title': 'Docker Containerization for Django Developers', 'url': 'https://www.youtube.com/watch?v=S8V77gqPezQ', 'desc': 'Containerizing database and web server.'}]
                }
            }
        ]
        CURRICULUM_CATALOG['Backend Developer']['projects'] = [
            {
                'title': 'Personal Contact Keeper CLI',
                'difficulty': 'Beginner',
                'description': 'Build a Python CLI application to perform CRUD operations on contacts using a SQLite database.',
                'technologies': 'Python, SQLite',
                'milestones': '- Setup SQLite connection\n- Write queries for inserting, listing, and updating records\n- Implement terminal command-line interface menu'
            },
            CURRICULUM_CATALOG['Full Stack Developer']['projects'][1], # Kanban Board
            {
                'title': 'E-Commerce Backend REST API',
                'difficulty': 'Advanced',
                'description': 'A fully secured backend API for shopping cart systems, product listings, orders, and Stripe mock integrations.',
                'technologies': 'Python, Django REST Framework, SQLite/PostgreSQL, Stripe API',
                'milestones': '- Build relational models for Category, Product, Order, OrderItem\n- Add token authentication\n- Write order completion logic with Stripe payments webhooks\n- Document endpoints with Swagger UI'
            }
        ]

    # Data Scientist
    if not CURRICULUM_CATALOG['Data Scientist']['weeks_data']:
        CURRICULUM_CATALOG['Data Scientist']['weeks_data'] = [
            {
                'title': 'Python Fundamentals for Data Science',
                'description': 'Learn Python structures (lists, tuples, dicts), comprehension, control loops, functions, and reading CSV files.',
                'tags': ['Python'],
                'resources': {
                    'Video': [{'title': 'Python for Data Science Course', 'url': 'https://www.youtube.com/watch?v=LHBE6Q9XlzI', 'desc': 'Fast track guide for scientists.'}]
                }
            },
            {
                'title': 'Scientific Libraries: NumPy and Pandas',
                'description': 'Master data arrays, Series, DataFrames, filters, groupings, handling missing data, and file import/exports.',
                'tags': ['Python', 'Pandas'],
                'resources': {
                    'Video': [{'title': 'Pandas Complete Tutorial', 'url': 'https://www.youtube.com/watch?v=vmEHCJofslg', 'desc': 'Learn Pandas methods in 2 hours.'}],
                    'Reading': [{'title': 'Pandas Official Tutorials', 'url': 'https://pandas.pydata.org/docs/user_guide/10min.html', 'desc': '10-minute guide to Pandas.'}]
                }
            },
            {
                'title': 'Data Visualization & Reporting',
                'description': 'Transform numbers into charts. Learn Matplotlib, Seaborn, plotting grids, distributions, and customize graphs.',
                'tags': ['Python'],
                'resources': {
                    'Video': [{'title': 'Data Visualization Crash Course', 'url': 'https://www.youtube.com/watch?v=a9UrKTVEeZA', 'desc': 'Learn how to construct plots.'}]
                }
            },
            {
                'title': 'SQL for Data Wrangling & Analysis',
                'description': 'Query real-world relational databases. Write aggregations, filters, joins, and connect python engines via SQLAlchemy.',
                'tags': ['SQL'],
                'resources': {
                    'Reading': [{'title': 'Kaggle: Intro to SQL', 'url': 'https://www.kaggle.com/learn/intro-to-sql', 'desc': 'Interactive database course on Kaggle.'}]
                }
            },
            {
                'title': 'Applied Statistics & Probability',
                'description': 'Learn distributions, hypothesis testing (t-test, ANOVA), correlation, p-values, and linear regressions.',
                'tags': ['Python'],
                'resources': {
                    'Video': [{'title': 'Statistics for Data Science', 'url': 'https://www.youtube.com/watch?v=XXistFTupfg', 'desc': 'Introduction to descriptive and inferential statistics.'}]
                }
            },
            {
                'title': 'Introduction to Machine Learning (Scikit-Learn)',
                'description': 'Understand supervised learning. Build Classification (decision trees) and Regression (linear regression) models.',
                'tags': ['Machine Learning'],
                'resources': {
                    'Video': [{'title': 'Scikit-Learn Machine Learning Course', 'url': 'https://www.youtube.com/watch?v=pqNCD_5r0QA', 'desc': 'Model fitting and testing tutorials.'}]
                }
            },
            {
                'title': 'Exploratory Data Analysis (EDA)',
                'description': 'Perform end-to-end data analysis on raw datasets. Perform cleaning, outlier detection, correlations, and build summary profiles.',
                'tags': ['Pandas'],
                'resources': {
                    'Reading': [{'title': 'Complete Guide to EDA', 'url': 'https://towardsdatascience.com/exploratory-data-analysis-eda-a-practical-guide-and-templates-for-structured-data-8c8cf7de7714', 'desc': 'Best practices for structured data.'}]
                }
            },
            {
                'title': 'Data Dashboard Deployment (Streamlit)',
                'description': 'Host your analysis. Write interactive Python scripts using Streamlit, build sliders, and deploy to Streamlit Cloud.',
                'tags': ['Python'],
                'resources': {
                    'Video': [{'title': 'Build a Data Dashboard with Streamlit', 'url': 'https://www.youtube.com/watch?v=ZZ4B0xg1Q53', 'desc': 'Interactive dashboards code tutorial.'}]
                }
            }
        ]
        CURRICULUM_CATALOG['Data Scientist']['projects'] = [
            {
                'title': 'E-Commerce Customer Segmentation',
                'difficulty': 'Beginner',
                'description': 'Wrangle a retail dataset in Jupyter Notebooks to clean missing entries and display top customer segments.',
                'technologies': 'Python, Jupyter, Pandas, Matplotlib',
                'milestones': '- Load raw transaction dataset\n- Clean nulls and correct data types\n- Generate charts on sales trends\n- Write insights summary markdown'
            },
            {
                'title': 'Real Estate Price Prediction Model',
                'difficulty': 'Intermediate',
                'description': 'Train a regression algorithm to predict house prices based on attributes like location, square footage, and rooms.',
                'technologies': 'Python, Scikit-Learn, Pandas, Seaborn',
                'milestones': '- Perform feature engineering on locations\n- Split dataset into training/testing sets\n- Evaluate linear regression and random forest models\n- Plot prediction accuracy residuals'
            },
            {
                'title': 'COVID-19 Dynamic Dashboard App',
                'difficulty': 'Advanced',
                'description': 'Build and deploy a dashboard presenting Covid-19 infection timelines, maps, and predictive models.',
                'technologies': 'Python, Pandas, Streamlit, Plotly, Streamlit Cloud',
                'milestones': '- Fetch live CSV dataset feeds\n- Create interactive geographical scatter maps in Plotly\n- Implement inputs to filter charts by country\n- Deploy code to Streamlit Cloud public URL'
            }
        ]

    # Fill default for Machine Learning, Mobile App, DevOps, Cybersecurity
    # if empty, map from appropriate catalog keys or seed standard blocks.
    # For now, let's copy matching blocks or stub templates if the user selects them, 
    # but let's write high-quality custom entries for them too!
    
    if not CURRICULUM_CATALOG['Machine Learning Engineer']['weeks_data']:
        CURRICULUM_CATALOG['Machine Learning Engineer']['weeks_data'] = [
            CURRICULUM_CATALOG['Data Scientist']['weeks_data'][0], # Python
            CURRICULUM_CATALOG['Data Scientist']['weeks_data'][1], # NumPy/Pandas
            CURRICULUM_CATALOG['Data Scientist']['weeks_data'][5], # Intro to ML
            {
                'title': 'Supervised Machine Learning Algorithms',
                'description': 'Learn mathematical implementations of SVMs, Random Forests, Naive Bayes, Gradient Boosting, and evaluate models using confusion matrices.',
                'tags': ['Machine Learning'],
                'resources': {'Video': [{'title': 'Supervised ML Algorithms', 'url': 'https://www.youtube.com/watch?v=Gv9_4yM81RA', 'desc': 'Complete overview of classic algorithms.'}]}
            },
            {
                'title': 'Unsupervised ML & Feature Engineering',
                'description': 'Implement K-Means clustering, Principal Component Analysis (PCA) dimensionality reduction, and scaling features.',
                'tags': ['Machine Learning'],
                'resources': {'Reading': [{'title': 'Intro to Feature Engineering', 'url': 'https://www.kaggle.com/learn/feature-engineering', 'desc': 'Kaggle course on feature transformations.'}]}
            },
            {
                'title': 'Deep Learning & Neural Networks',
                'description': 'Build basic Artificial Neural Networks (ANN) using PyTorch or TensorFlow. Learn forward and backward propagation.',
                'tags': ['Machine Learning'],
                'resources': {'Video': [{'title': 'PyTorch for Beginners', 'url': 'https://www.youtube.com/watch?v=V_xro1bcAuA', 'desc': 'Hands-on neural network coding course.'}]}
            },
            {
                'title': 'NLP & Convolutional Networks',
                'description': 'Understand CNNs for image classification and Transformers or RNNs for natural language processing.',
                'tags': ['Machine Learning'],
                'resources': {'Video': [{'title': 'CNNs and Computer Vision Tutorial', 'url': 'https://www.youtube.com/watch?v=zfiSAzpy9LI', 'desc': 'Learn image recognition structures.'}]}
            },
            {
                'title': 'MLOps & Model Deployment (FastAPI & Docker)',
                'description': 'Wrap models in FastAPI JSON endpoints, containerize using Docker, and launch on AWS Elastic Beanstalk.',
                'tags': ['Docker', 'Machine Learning'],
                'resources': {'Video': [{'title': 'FastAPI Model Deployment', 'url': 'https://www.youtube.com/watch?v=gQ-G-wU2mXY', 'desc': 'Serving models via API endpoints.'}]}
            }
        ]
        CURRICULUM_CATALOG['Machine Learning Engineer']['projects'] = [
            CURRICULUM_CATALOG['Data Scientist']['projects'][1], # House Price
            {
                'title': 'Spam Email Classification Classifier',
                'difficulty': 'Intermediate',
                'description': 'Train a text-processing Naive Bayes model to detect spam messages.',
                'technologies': 'Python, Scikit-Learn, NLTK',
                'milestones': '- Clean and tokenize text inputs\n- Vectorize inputs with TF-IDF\n- Train classification model\n- Check precision and recall metrics'
            },
            {
                'title': 'Image Classification API Service',
                'difficulty': 'Advanced',
                'description': 'Deploy a PyTorch neural network classifying custom images inside Docker containers via FastAPI.',
                'technologies': 'Python, PyTorch, FastAPI, Docker',
                'milestones': '- Train PyTorch model on MNIST/CIFAR\n- Build FastAPI backend routes\n- Write Dockerfile configurations\n- Spin up local containers and test endpoint requests'
            }
        ]

    # Map the rest with similar robust mappings so that all choice cards work perfectly!
    for key in ['Mobile App Developer', 'DevOps Engineer', 'Cybersecurity Specialist']:
        if not CURRICULUM_CATALOG[key]['weeks_data']:
            # Stub some default content using general modules
            CURRICULUM_CATALOG[key]['weeks_data'] = [
                {
                    'title': f'Introduction to {key} & Essentials',
                    'description': f'Learn the primary tools, concepts, and setups required to excel as a professional {key}.',
                    'tags': ['Git'],
                    'resources': {'Video': [{'title': f'Getting Started with {key}', 'url': 'https://www.youtube.com/', 'desc': f'Introductory guide.'}]}
                },
                CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][1], # JS/Prog
                CURRICULUM_CATALOG['Full Stack Developer']['weeks_data'][2], # Git
                {
                    'title': f'Core {key} Frameworks & Workflows',
                    'description': f'Deep dive into the core commands, structures, and environments of {key}.',
                    'tags': ['Git'],
                    'resources': {'Reading': [{'title': f'{key} Tutorials', 'url': 'https://google.com/', 'desc': f'Framework docs.'}]}
                },
                {
                    'title': f'Integrating Data & APIs in {key}',
                    'description': 'Learn how databases and networks connect, fetch JSON objects, and handle data storage.',
                    'tags': ['APIs'],
                    'resources': {'Reading': [{'title': 'REST API Basics', 'url': 'https://google.com/', 'desc': 'API communication guidelines.'}]}
                },
                {
                    'title': f'Advanced Security & System Layouts in {key}',
                    'description': 'Examine safety operations, encrypted connections, authentication, and vulnerability checks.',
                    'tags': ['Git'],
                    'resources': {'Video': [{'title': 'System Security Guide', 'url': 'https://www.youtube.com/', 'desc': 'Security strategies.'}]}
                },
                {
                    'title': f'{key} Testing & Quality Control',
                    'description': 'Learn to write unit tests, integration validation scripts, and debug syntax issues.',
                    'tags': ['Git'],
                    'resources': {'Practice': [{'title': 'Testing Guidelines', 'url': 'https://google.com/', 'desc': 'Automating checks.'}]}
                },
                {
                    'title': f'Deployment & Cloud Systems for {key}',
                    'description': 'Deploy finished products to app marketplaces, server nodes, or web hosting platforms.',
                    'tags': ['Docker'],
                    'resources': {'Video': [{'title': 'Cloud Deployments', 'url': 'https://www.youtube.com/', 'desc': 'Global setup details.'}]}
                }
            ]
            CURRICULUM_CATALOG[key]['projects'] = [
                {
                    'title': f'Simple {key} Dashboard',
                    'difficulty': 'Beginner',
                    'description': f'Scaffold the baseline directory structure and build a local setup simulating {key} tasks.',
                    'technologies': 'Python, Git, Markdown',
                    'milestones': '- Configure workspace environment\n- Set up local Git repository\n- Write documentation in README'
                },
                {
                    'title': f'Collaborative {key} Tool',
                    'difficulty': 'Intermediate',
                    'description': f'Assemble an interactive utility incorporating API hooks and data models for student trackers.',
                    'technologies': 'Python, SQLite, APIs',
                    'milestones': '- Build relational schema\n- Connect data feeds\n- Construct tests'
                },
                {
                    'title': f'Enterprise {key} Platform',
                    'difficulty': 'Advanced',
                    'description': f'Implement a fully scalable cloud hosted system featuring container deployments, authentication, and secure databases.',
                    'technologies': 'Docker, AWS/Render, PostgreSQL',
                    'milestones': '- Write custom configuration scripts\n- Setup cloud servers\n- Build analytics reporting'
                }
            ]

setup_curriculums()

def generate_roadmap(profile, cleaned_data):
    # Ensure catalogs are ready
    setup_curriculums()
    
    career_target = cleaned_data['career_target']
    experience_level = cleaned_data['experience_level']
    learning_style = cleaned_data['preferred_learning_mode']
    study_hours = float(cleaned_data['study_hours_per_day'])
    
    # 1. Determine duration of path based on study hours per day
    if study_hours < 2.0:
        duration_weeks = 8
    elif study_hours < 4.0:
        duration_weeks = 6
    else:
        duration_weeks = 4

    # 2. Update Student Profile
    profile.full_name = cleaned_data['full_name']
    profile.education_level = cleaned_data['education_level']
    profile.career_target = career_target
    profile.study_hours_per_day = study_hours
    profile.experience_level = experience_level
    profile.learning_style = learning_style
    profile.interests = cleaned_data.get('interests', '')
    profile.points += 100 # Award points for generating a path
    profile.save()
    
    # Associate chosen skills
    known_skills = cleaned_data.get('current_skills', [])
    if known_skills:
        profile.skills.set(known_skills)
        
    # Process new skills typed by user (separated by commas)
    new_skills_text = cleaned_data.get('new_skills_text', '')
    if new_skills_text:
        for sk_name in new_skills_text.split(','):
            sk_name = sk_name.strip()
            if sk_name:
                skill_obj, created = Skill.objects.get_or_create(name=sk_name)
                profile.skills.add(skill_obj)
    
    # 3. Deactivate other paths of this user
    LearningPath.objects.filter(student=profile, is_active=True).update(is_active=False)
    
    # 4. Create new LearningPath
    path_title = f"{experience_level} to Pro: {career_target} Roadmap"
    learning_path = LearningPath.objects.create(
        student=profile,
        title=path_title,
        career_target=career_target,
        duration_weeks=duration_weeks,
        is_active=True
    )
    
    # 5. Extract weeks content from Catalog
    catalog_path = CURRICULUM_CATALOG.get(career_target, CURRICULUM_CATALOG['Full Stack Developer'])
    catalog_weeks = catalog_path['weeks_data']
    
    # If student is Intermediate or Advanced, we customize!
    # Beginner: weeks_to_generate = all weeks
    # Intermediate: we still generate all weeks but we can auto-complete or mark basic modules
    # as "Completed" immediately based on user's known skills.
    # Let's adjust catalog weeks length to match duration_weeks
    # If duration_weeks is 4: we combine weeks (1+2, 3+4, 5+6, 7+8)
    # If duration_weeks is 6: we compress (1, 2, 3+4, 5, 6, 7+8)
    # If duration_weeks is 8: we use 1 to 1 mapping
    
    generated_weeks_data = []
    if duration_weeks == 8:
        generated_weeks_data = catalog_weeks[:8]
    elif duration_weeks == 6:
        # Combine some intermediate weeks
        if len(catalog_weeks) >= 8:
            generated_weeks_data = [
                catalog_weeks[0], # Week 1
                catalog_weeks[1], # Week 2
                {
                    'title': f"{catalog_weeks[2]['title']} & {catalog_weeks[3]['title']}",
                    'description': f"{catalog_weeks[2]['description']} Also, {catalog_weeks[3]['description']}",
                    'tags': list(set(catalog_weeks[2]['tags'] + catalog_weeks[3]['tags'])),
                    'resources': merge_resources(catalog_weeks[2]['resources'], catalog_weeks[3]['resources'])
                }, # Week 3
                catalog_weeks[4], # Week 4
                catalog_weeks[5], # Week 5
                {
                    'title': f"{catalog_weeks[6]['title']} & {catalog_weeks[7]['title']}",
                    'description': f"{catalog_weeks[6]['description']} Furthermore, {catalog_weeks[7]['description']}",
                    'tags': list(set(catalog_weeks[6]['tags'] + catalog_weeks[7]['tags'])),
                    'resources': merge_resources(catalog_weeks[6]['resources'], catalog_weeks[7]['resources'])
                } # Week 6
            ]
        else:
            generated_weeks_data = catalog_weeks
    else: # duration_weeks == 4
        # Combine every two weeks
        if len(catalog_weeks) >= 8:
            generated_weeks_data = [
                {
                    'title': f"{catalog_weeks[0]['title']} & {catalog_weeks[1]['title']}",
                    'description': f"{catalog_weeks[0]['description']} {catalog_weeks[1]['description']}",
                    'tags': list(set(catalog_weeks[0]['tags'] + catalog_weeks[1]['tags'])),
                    'resources': merge_resources(catalog_weeks[0]['resources'], catalog_weeks[1]['resources'])
                }, # Week 1
                {
                    'title': f"{catalog_weeks[2]['title']} & {catalog_weeks[3]['title']}",
                    'description': f"{catalog_weeks[2]['description']} {catalog_weeks[3]['description']}",
                    'tags': list(set(catalog_weeks[2]['tags'] + catalog_weeks[3]['tags'])),
                    'resources': merge_resources(catalog_weeks[2]['resources'], catalog_weeks[3]['resources'])
                }, # Week 2
                {
                    'title': f"{catalog_weeks[4]['title']} & {catalog_weeks[5]['title']}",
                    'description': f"{catalog_weeks[4]['description']} {catalog_weeks[5]['description']}",
                    'tags': list(set(catalog_weeks[4]['tags'] + catalog_weeks[5]['tags'])),
                    'resources': merge_resources(catalog_weeks[4]['resources'], catalog_weeks[5]['resources'])
                }, # Week 3
                {
                    'title': f"{catalog_weeks[6]['title']} & {catalog_weeks[7]['title']}",
                    'description': f"{catalog_weeks[6]['description']} {catalog_weeks[7]['description']}",
                    'tags': list(set(catalog_weeks[6]['tags'] + catalog_weeks[7]['tags'])),
                    'resources': merge_resources(catalog_weeks[6]['resources'], catalog_weeks[7]['resources'])
                } # Week 4
            ]
        else:
            generated_weeks_data = catalog_weeks

    # 6. Create modules, recommendations, and initial progresses in database
    student_skills_names = [s.name.lower() for s in profile.skills.all()]
    
    for i, w in enumerate(generated_weeks_data, start=1):
        module = Module.objects.create(
            learning_path=learning_path,
            week_number=i,
            title=w['title'],
            description=w['description'],
            order=i
        )
        
        # Check if the student already knows all skills associated with this module
        module_skills = [t.lower() for t in w.get('tags', [])]
        knows_all_skills = len(module_skills) > 0 and all(ms in student_skills_names for ms in module_skills)
        
        # Create Progress record
        initial_status = 'Completed' if knows_all_skills else 'Not Started'
        Progress.objects.create(
            student=profile,
            module=module,
            status=initial_status
        )
        
        # Filter and create Recommendations based on preferred learning style
        # Styles: Video, Reading, Practice, Mixed
        all_resources = w.get('resources', {})
        selected_resources = []
        
        if learning_style == 'Video':
            selected_resources = all_resources.get('Video', [])
        elif learning_style == 'Reading':
            selected_resources = all_resources.get('Reading', [])
        elif learning_style == 'Practice':
            selected_resources = all_resources.get('Practice', [])
        else: # Mixed
            # Take one of each type
            for r_type in ['Video', 'Reading', 'Practice']:
                res_list = all_resources.get(r_type, [])
                if res_list:
                    selected_resources.append(res_list[0])
                    
        # Write resources to db
        for r in selected_resources:
            # Detect resource type
            res_type = 'Course'
            url = r['url']
            if 'youtube.com' in url or 'youtu.be' in url:
                res_type = 'Video'
            elif 'docs' in url or 'developer.mozilla' in url:
                res_type = 'Reading'
            elif 'freecodecamp' in url or 'codewars' in url or 'sqlbolt' in url or 'learngit' in url:
                res_type = 'Practice'
                
            Recommendation.objects.create(
                module=module,
                title=r['title'],
                resource_type=res_type,
                url=url,
                description=r['desc'] if 'desc' in r else ''
            )
            
    # 7. Create Project Suggestions
    for proj in catalog_path.get('projects', []):
        ProjectSuggestion.objects.create(
            learning_path=learning_path,
            title=proj['title'],
            description=proj['description'],
            difficulty=proj['difficulty'],
            milestones=proj['milestones'],
            technologies=proj['technologies']
        )
        
    # Check & award milestone badge for starting a path
    award_badge_by_type(profile, 'path_creation')
    
    return learning_path

def merge_resources(res1, res2):
    merged = {}
    for r_type in ['Video', 'Reading', 'Practice']:
        merged[r_type] = res1.get(r_type, []) + res2.get(r_type, [])
    return merged

def award_badge_by_type(profile, badge_type):
    # Ensure badges are seeded
    badges_mapping = {
        'path_creation': {
            'name': 'The Journey Begins',
            'description': 'Created your first personalized learning roadmap.',
            'icon': 'fa-solid fa-compass'
        },
        'streak_5': {
            'name': 'Consistency Champ',
            'description': 'Achieved a daily streak of 5 days.',
            'icon': 'fa-solid fa-fire'
        },
        'completion_1': {
            'name': 'First Milestone',
            'description': 'Completed your first weekly learning module.',
            'icon': 'fa-solid fa-circle-check'
        },
        'path_completion': {
            'name': 'Career Architect',
            'description': 'Successfully completed 100% of an active learning path.',
            'icon': 'fa-solid fa-graduation-cap'
        },
        'points_500': {
            'name': 'Knowledge Collector',
            'description': 'Earned a total of 500 experience points.',
            'icon': 'fa-solid fa-trophy'
        }
    }
    
    if badge_type in badges_mapping:
        data = badges_mapping[badge_type]
        badge, created = Badge.objects.get_or_create(
            name=data['name'],
            defaults={'description': data['description'], 'badge_type': badge_type, 'icon': data['icon']}
        )
        # Check if already earned
        if not StudentBadge.objects.filter(student=profile, badge=badge).exists():
            StudentBadge.objects.create(student=profile, badge=badge)
            profile.points += 50
            profile.save()
            return badge
    return None
