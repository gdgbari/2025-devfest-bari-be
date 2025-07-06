import { Group } from "@modelsGroup";

export interface UserProfile {
    userId: string;
    nickname: string;
    name: string;
    surname: string;
    email: string;
    groupId: string | null;
    group: Group | null;
    position: number | null;
    score: number | null;
    role: string | null;
}