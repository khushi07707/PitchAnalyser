using System;

namespace AIAugmentedPitchAnalyzer.Shared.Responses
{
    /// <summary>
    /// Standardized API response wrapper.
    /// </summary>
    /// <typeparam name="T">Payload type</typeparam>
    public class ApiResponse<T>
    {
        public bool Success { get; set; } = true;
        public string? Message { get; set; }
        public T? Data { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }
}
