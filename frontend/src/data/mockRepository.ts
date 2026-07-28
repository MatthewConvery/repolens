import type { Finding } from "../compontents/layout/dashboard/RecentFindings";

export const repositoryStats = [
    {
        label: "Files",
        value: "248",
        description: "Accross 32 directories"
    },
    {
        label: "Functions",
        value: "1,126",
        description: "87 exported"
    },
    {
        label: "Classes",
        value: "84",
        description: "12 abstract"
    },
    {
        label: "Tests",
        value: "196",
        description: "42 test files"
    },
    {
        label: "Coverage",
        value: "72%",
        description: "Target is 80%"
    },
    {
        label: "Repository Health",
        value: "87/100",
        description: "Good overall condition"
    }
];

export type BriefingItem = {
    text: string,
    type: "success" | "warning" | "info";
};

export const repositoryBriefing: {
    summary: string;
    items: BriefingItem[];
} = {
    summary: "RepoLens is a React and TypeScript application designed to help developers understand unfamiliar repositories before making changes.",

    items: [
        {
            text: "The frontend is organised around reusable layout and dashboard comonents.",
            type: "success"
        },
        {
            text: "Repository statistics are currently using mock data.",
            type: "info"
        },
        {
            text: "No backend connection or repository analysis is available yet.",
            type: "warning"
        },
        {
            text: "The next major ticket is connecting the dashboard to real repository data.",
            type: "info"
        }
    ]
};

export const recentFindings: Finding[] = [
    {
        id: 1,
        file: "src/services/AuthService.ts",
        message: "Possible null reference before accessing the user object.",
        severity: "critical"
    },
    {
        id: 2,
        file: "src/parsers/RepositoryParser.ts",
        message: "Function exceeds the recommended maximum length.",
        severity: "warning"
    },
    {
        id: 3,
        file: "src/search/SearchIndex.ts",
        message: "Repository indexing completed successfully.",
        severity: "success"
    },
    {
        id: 4,
        file: "src/config/ConfigLoader.ts",
        message: "Public function is missing documentation.",
        severity: "info"
    }
];