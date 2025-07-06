import {Group} from "@modelsGroup";
import {LeaderboardUserEntry} from "@modelsLeaderboardUserEntry";

export interface Leaderboard {
    currentUser: LeaderboardUserEntry | null;
    users: Array<LeaderboardUserEntry>;
    groups: Array<Group>;
}
