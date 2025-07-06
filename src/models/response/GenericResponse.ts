import { GenericResponseError } from './GenericResponseError';

export interface GenericResponse<T> {
    error: GenericResponseError | null;
    data: T | null;
}