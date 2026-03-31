# Frontend Setup Guide

The Frontend is a Next.js React application that provides the user interface for the CenQuery project, allowing users to submit natural language questions and view query results.

## Prerequisites

- Node.js 18 or higher
- npm (comes with Node.js) or yarn
- Backend API running (see [Backend Setup](../Backend/README.md))

## Installation

### 1. Navigate to Frontend Directory

```bash
cd Applications/Frontend
```

### 2. Install Dependencies

```bash
# Using npm
npm install

# Or using yarn
yarn install
```

## Configuration

### Environment Variables

Create a `.env.local` file in the Frontend folder with the following variables:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_PATH=/api

# Application Settings
NEXT_PUBLIC_APP_NAME=CenQuery
NEXT_PUBLIC_APP_DESCRIPTION=Natural Language SQL Query Generation
```

### Tailwind CSS & PostCSS

The project is configured with:
- **Tailwind CSS v4** for styling
- **PostCSS** for CSS processing
- **Lucide React** for icons
- **Framer Motion** for animations
- **Recharts** for data visualization

Configuration files:
- `tailwind.config.ts` - Tailwind customization
- `postcss.config.mjs` - PostCSS settings

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
npm start
```

## Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run ESLint to check code quality
npm run lint
```

## Project Structure

```
Frontend/
├── src/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   ├── pages/           # Page routes
│   └── styles/          # Global styles
├── public/              # Static assets
├── components.json      # Component configuration
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript configuration
├── next.config.ts       # Next.js configuration
├── tailwind.config.ts   # Tailwind CSS configuration
├── postcss.config.mjs   # PostCSS configuration
└── eslint.config.mjs    # ESLint configuration
```

## Development Notes

### Key Technologies

- **Next.js 16.1.7** - React framework
- **React 19.2.3** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Utility-first CSS
- **Framer Motion** - Animation library
- **Radix UI** - Headless UI components

### Directory Conventions

- Components go in `src/components/`
- Pages go in `src/app/`
- Styles in `src/styles/`

### Code Quality

```bash
# Check code with ESLint
npm run lint

# Fix linting issues
npm run lint --fix
```

## API Integration

The frontend communicates with the Backend API at the URL specified in `NEXT_PUBLIC_API_URL`:

### Main API Endpoints Used

- `POST /api/generate-sql` - Generate SQL from question
- `POST /api/execute-sql` - Execute generated SQL

Example request:

```javascript
// Generate SQL from question
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/generate-sql`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'What is the total count of patients?' })
});

const data = await response.json();
console.log(data.sql_query);
```

## Troubleshooting

### Port 3000 Already in Use

```bash
# Use a different port
npm run dev -- -p 3001
```

### API Connection Issues

- Ensure Backend is running at `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS settings in Backend API
- Check browser console for network errors

### Build Error: Module Not Found

```bash
# Clear cache and reinstall dependencies
rm -rf node_modules .next
npm install
npm run build
```

### TypeScript Errors

```bash
# Check TypeScript compilation
npx tsc --noEmit
```

## Performance Optimization

- Images are optimized with Next.js Image component
- CSS is purged of unused styles in production
- Dynamic imports for code splitting

## Deployment

The frontend can be deployed to:
- **Vercel** (Recommended for Next.js)
- **Netlify**
- **AWS S3 + CloudFront**
- **Docker container**
- **Traditional web servers**

### Vercel Deployment

```bash
npm install -g vercel
vercel
```

### Docker Deployment

```bash
docker build -t cenquery-frontend .
docker run -p 3000:3000 cenquery-frontend
```

## See Also

- [Backend Setup](../Backend/README.md) - API server
- [LLM-Engine Setup](../LLM-Engine/README.md) - Query generation engine
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
