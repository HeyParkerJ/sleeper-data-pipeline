import { APIGatewayEvent, Context } from 'aws-lambda';

export const lambda_handler = async (event: APIGatewayEvent, context: Context) => {
    return {
        statusCode: 200,
        body: JSON.stringify({ message: "Hello, TypeScript Lambda!" }),
    };
};

