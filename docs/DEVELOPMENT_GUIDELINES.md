# 📚 Kloud Cloud - Development Guidelines

## Quick Start

```bash
# Clone repository
git clone https://github.com/LedjanAhmati/Kloud-cloud.git
cd Kloud-cloud

# Setup Python environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1 # Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
docker compose up -d
```

## Project Structure

```
Kloud-cloud/
├── apps/
│   ├── api/              # FastAPI Backend
│   └── web/              # Next.js Frontend
├── backend/
│   └── layers/           # 18-Layer Architecture
│       ├── layer1-core/
│       ├── layer2-ddos/
│       ├── ...
│       └── layer18-config/
├── ocean-core/           # Curiosity Ocean AI
├── services/             # Microservices
├── modules/              # Shared Modules
├── docs/                 # Documentation
└── docker-compose.yml    # Container orchestration
```

## Coding Standards

### Python
- **Formatter**: Black
- **Imports**: isort
- **Linting**: flake8, mypy
- **Docstrings**: Google style

```python
def process_data(input: str, options: dict | None = None) -> dict:
    """Process input data with given options.
    
    Args:
        input: The raw input string
        options: Optional configuration dictionary
        
    Returns:
        Processed data as dictionary
        
    Raises:
        ValueError: If input is empty
    """
    if not input:
        raise ValueError("Input cannot be empty")
    return {"result": input.strip()}
```

### TypeScript
- **Formatter**: Prettier
- **Linting**: ESLint
- **Style**: Functional components, typed props

```typescript
interface UserProps {
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

export const UserCard: React.FC<UserProps> = ({ name, email, role }) => {
  return (
    <div className="user-card">
      <h3>{name}</h3>
      <p>{email}</p>
      <span className={`badge-${role}`}>{role}</span>
    </div>
  );
};
```

## Git Workflow

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `hotfix/description` - Production fixes
- `docs/description` - Documentation

### Commit Messages (Conventional Commits)
```
<type>(<scope>): <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Examples:
feat(ocean): Add v2 API endpoints
fix(auth): Resolve JWT expiration issue
docs(api): Update endpoint documentation
```

## API Guidelines

### REST Endpoints
```
GET    /api/v1/resources      # List resources
GET    /api/v1/resources/:id  # Get single resource
POST   /api/v1/resources      # Create resource
PUT    /api/v1/resources/:id  # Update resource
DELETE /api/v1/resources/:id  # Delete resource
```

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2026-02-03T12:00:00Z",
    "version": "1.0.0"
  }
}
```

### Error Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

## Testing

### Python
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps/api --cov-report=html

# Run specific test
pytest tests/test_auth.py -v
```

### TypeScript
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Environment Variables

Create `.env` file from `.env.example`:

```env
# Server
NODE_ENV=development
PORT=8000

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=klouddb
POSTGRES_USER=kloud
POSTGRES_PASSWORD=your-password

# Redis
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=your-super-secret-key
JWT_EXPIRES_IN=24h

# AI
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

## Deployment

### Development
```bash
docker compose up -d
```

### Production
```bash
docker compose -f docker-compose.prod.yml up -d
```

### CI/CD
GitHub Actions workflow runs:
1. Lint & Type Check
2. Unit Tests
3. Build Docker Images
4. Deploy to Staging
5. (Manual) Deploy to Production

---

## Need Help?

- 📖 [Architecture Docs](./ARCHITECTURE.md)
- 🔧 [API Reference](./API_GUIDELINES.md)
- 🚀 [Deployment Guide](./DEPLOYMENT.md)
- 💬 Contact: support@kloud.cloud

*Kloud Cloud Platform © 2026 ABA GmbH*

