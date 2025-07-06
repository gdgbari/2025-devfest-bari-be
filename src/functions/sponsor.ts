import * as functions from "firebase-functions";
import { Sponsor } from "@models/Sponsor";
import { db } from "../index";
import { serializedErrorResponse, serializedSuccessResponse, serializedExceptionResponse } from "../utils/responseHelper";

export const getSponsorList = functions.https.onCall(async (_, context) => {
    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "The request has to be authenticated.");
    }

    try {
        const sponsorsSnapshot = await db.collection("sponsors").get();

        if (!sponsorsSnapshot) {
            return serializedErrorResponse("sponsors-not-found", "No sponsors found.");
        }

        const sponsorList = await Promise.all(
            sponsorsSnapshot.docs.map(async (sponsorDoc) => {
                const sponsorData = sponsorDoc.data();

                const sponsor: Sponsor = {
                    sponsorId: sponsorDoc.id,
                    name: sponsorData.name,
                    description: sponsorData.description,
                    websiteUrl: sponsorData.websiteUrl,
                };

                return serializedSuccessResponse(sponsor);
            })
        );

        return serializedSuccessResponse(sponsorList);
    } catch (error) {
        console.error("An error occurred while fetching the sponsor list.", error);
        return serializedExceptionResponse(error);
    }
});
