using System;
using System.Net;
using System.Text.Json;
using System.Threading.Tasks;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;

namespace AIAugmentedPitchAnalyzer.Api.Middleware
{
    /// <summary>
    /// Middleware to catch unhandled exceptions globally and return standard ApiResponse schema.
    /// </summary>
    public class ExceptionHandlingMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<ExceptionHandlingMiddleware> _logger;

        public ExceptionHandlingMiddleware(RequestDelegate next, ILogger<ExceptionHandlingMiddleware> logger)
        {
            _next = next;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            try
            {
                await _next(context);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "An unhandled exception occurred during request execution on path: {Path}", context.Request.Path);
                await HandleExceptionAsync(context, ex);
            }
        }

        private static Task HandleExceptionAsync(HttpContext context, Exception exception)
        {
            context.Response.ContentType = "application/json";
            
            var statusCode = (int)HttpStatusCode.InternalServerError;
            var message = "An internal server error occurred.";

            // Map custom exception types
            if (exception is UnauthorizedAccessException)
            {
                statusCode = (int)HttpStatusCode.Unauthorized;
                message = "Unauthorized access.";
            }
            else if (exception is ArgumentException || exception is InvalidOperationException)
            {
                statusCode = (int)HttpStatusCode.BadRequest;
                message = exception.Message;
            }
            else if (exception is FileNotFoundException)
            {
                statusCode = (int)HttpStatusCode.NotFound;
                message = "Requested file resource not found.";
            }
            else
            {
                // In Development or Debug, return raw error details
                message = exception.Message;
            }

            context.Response.StatusCode = statusCode;

            var response = new ApiResponse<object>
            {
                Success = false,
                Message = message
            };

            var jsonOptions = new JsonSerializerOptions 
            { 
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase 
            };
            var result = JsonSerializer.Serialize(response, jsonOptions);
            return context.Response.WriteAsync(result);
        }
    }
}
