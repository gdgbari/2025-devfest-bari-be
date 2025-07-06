export interface Question {
    questionId: string;
    text: string;
    answerList: string[];
    correctAnswer: string | null;
    value: number | null;
}
