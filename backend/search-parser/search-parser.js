import booleanParser from 'boolean-parser';

/*
Based on https://github.com/avivr/search-parser
*/

/**
 * Helper function to remove one layer of surrounding quotes from a string.
 * It preserves any inner quotes.
 * @param {string} str - The string to process.
 * @returns {string} - The string without one layer of surrounding quotes.
 */
function removeSurroundingQuotes(str) {
    if ((str.startsWith('"') && str.endsWith('"')) || (str.startsWith("'") && str.endsWith("'"))) {
        return str.slice(1, -1);
    }
    return str;
}

/**
 * Helper function to extract key and value from an expression.
 * @param {string} expr - The expression to parse.
 * @returns {Object} - An object containing the key and processed value.
 */
function extractKeyValue(expr) {
    // Check if the expression contains a colon
    if (!expr.includes(':')) {
        // For freetext, preserve all quotes
        return {key: 'freetext', value: expr}; // Do we need to do expr.toLowerCase()
    }

    // For key-value expressions, remove one layer of surrounding quotes
    expr = removeSurroundingQuotes(expr);

    const parts = expr.split(':');
    const key = parts[0].trim();
    let rawValue = parts.slice(1).join(':').trim(); // Support values with colons

    // Determine if the value is quoted
    const isQuoted = (rawValue.startsWith('"') && rawValue.endsWith('"')) || (rawValue.startsWith("'") && rawValue.endsWith("'")) || (rawValue.startsWith("''") && rawValue.endsWith("''")) || (rawValue.startsWith('""') && rawValue.endsWith('""'));

    let value;

    if (isQuoted) {
        // Remove one additional layer of quotes from the value
        value = removeSurroundingQuotes(rawValue);
    } else {
        // If not quoted and part of a key-value expression, take only the first word
        value = rawValue.split(' ')[0];
    }

    return {key, value};
}

/**
 * Preprocesses the query to insert implicit ANDs between terms.
 * It ensures that spaces between terms are replaced with AND operators,
 * except when the space is within quotes or within key-value pairs.
 * @param {string} query - The original query string.
 * @returns {string} - The query string with implicit ANDs inserted.
 */
function insertImplicitANDs(query) {
    const tokens = [];
    let lastIndex = 0;

    // Enhanced regex to match:
    // 1. Key:value pairs with quoted values
    // 2. Standalone quoted phrases
    // 3. Unquoted words
    const tokenRegex = /(\b\w+:(?:"+[^"]*"+|'{'1,}[^']*'+)|"+[^"]*"+|'{'1,}[^']*'+|\S+)/g;
    let match;

    while ((match = tokenRegex.exec(query)) !== null) {
        const matchedToken = match[0];

        // Add any text before the match if necessary
        // Not needed here since the regex captures all tokens

        tokens.push(matchedToken);
        lastIndex = match.index + matchedToken.length;
    }

    const operators = new Set(['AND', 'OR', 'NOT']);
    const newTokens = [];

    for (let i = 0; i < tokens.length; i++) {
        const currentToken = tokens[i];
        const upperToken = currentToken.toUpperCase();

        if (i > 0) {
            const prevToken = tokens[i - 1];
            const upperPrev = prevToken.toUpperCase();

            // If neither the current nor the previous token is an operator, insert AND
            if (!operators.has(upperToken) && !operators.has(upperPrev)) {
                newTokens.push('AND');
            }
        }

        newTokens.push(currentToken);
    }

    return newTokens.join(' ');
}

/**
 * Parses the query string into filter objects.
 * @param {string} query - The query string to parse.
 * @returns {Array} - An array of filter objects.
 */
export function parseSearchQuery(query) {
    // Step 1: Insert implicit ANDs
    const processedQuery = insertImplicitANDs(query);

    // Step 2: Parse the boolean query
    const parsedBooleanQuery = booleanParser.parseBooleanQuery(processedQuery);

    /**
     * Converts parsed expressions into filter objects.
     * @param {Array} expressions - Array of parsed expressions.
     * @returns {Array} - Array of filter objects.
     */
    function toFilterObject(expressions) {
        return expressions.map(expr => {
            // Determine if the expression is an exclusion
            const isExclude = expr.toUpperCase().startsWith('NOT ');
            const collectionName = isExclude ? 'exclude' : 'include';

            // Remove 'NOT ' prefix if present
            const positiveExpr = isExclude ? expr.slice(4).trim() : expr.trim();

            // Extract key and value using the helper function
            const {key, value} = extractKeyValue(positiveExpr);

            return {
                [key]: {
                    [collectionName]: value,
                },
            };
        });
    }

    // Step 3: Convert all parsed expressions into filter objects
    return parsedBooleanQuery.map(toFilterObject);
}