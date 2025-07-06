import { GenericResponse } from "../models/response/GenericResponse";

export function serializedSuccessResponse(data: any): String {
    return JSON.stringify(successResponse(JSON.stringify(data)));
}

export function serializedErrorResponse(errorCode: String, details: String | null = null): String {
    return JSON.stringify(errorResponse(errorCode, details));
}

export function successResponse<T>(data: T): GenericResponse<T> {
    return {
        error: null,
        data: data,
    };
}

export function errorResponse<T>(errorCode: String, details: String | null = null): GenericResponse<T> {
    return {
        error: {
            errorCode: errorCode,
            details: details,
        },
        data: null,
    };
}

export function exceptionResponse<T>(error: any): GenericResponse<T> {
    if (error instanceof Error) {
        return errorResponse("internal", error.message);
    } else {
        return errorResponse("internal", "An unknown error occurred.");
    }
}

export function serializedExceptionResponse(error: any): String {
    return JSON.stringify(exceptionResponse(error));
}
