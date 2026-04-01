# Frontend Branch

This branch contains ONLY the frontend code for the Bug Bounty Platform.

## Structure
```
frontend/
├── src/
│   ├── app/          # Next.js app router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and API client
│   └── store/        # State management
├── public/           # Static assets
└── package.json      # Dependencies
```

## Tech Stack
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Zustand (State Management)

## Development
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8002
```

## Note
This is a feature branch. For the complete monorepo (frontend + backend + simulation), see the `main` branch.
