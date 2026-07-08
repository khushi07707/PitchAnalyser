using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Shared.Settings;
using Microsoft.Extensions.Options;
using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Infrastructure.Services
{
    public class OpenAIProvider : IAIProvider
    {
        private readonly HttpClient _httpClient;
        private readonly AISettings _settings;

        public OpenAIProvider(HttpClient httpClient, IOptions<AISettings> options)
        {
            _httpClient = httpClient;
            _settings = options.Value;

            if (string.IsNullOrWhiteSpace(_settings.ApiKey))
            {
                throw new InvalidOperationException("AISettings.ApiKey must be provided for OpenAI/Azure OpenAI.");
            }

            _httpClient.DefaultRequestHeaders.Clear();
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_settings.ApiKey}");
        }

        public async Task<IAIProviderResult> AnalyzeAsync(string prompt)
        {
            var requestBody = new
            {
                model = _settings.Model,
                messages = new[]
                {
                    new { role = "user", content = prompt }
                },
                temperature = 0.2,
                max_tokens = 800
            };

            var requestUri = GetRequestUri();
            var response = await _httpClient.PostAsJsonAsync(requestUri, requestBody);
            if (!response.IsSuccessStatusCode)
            {
                var error = await response.Content.ReadAsStringAsync();
                return new OpenAIProviderResult(false, string.Empty, string.Empty, 0, string.Empty, $"AI provider request failed: {response.StatusCode}. {error}");
            }

            var rawJson = await response.Content.ReadAsStringAsync();
            var parsedOutput = ExtractContent(rawJson);
            var analysisJson = JsonSerializer.Serialize(new
            {
                provider = _settings.Provider,
                model = _settings.Model,
                generatedAt = DateTime.UtcNow,
                output = parsedOutput.RawOutput,
                raw = JsonSerializer.Deserialize<JsonElement>(rawJson)
            }, new JsonSerializerOptions { WriteIndented = true });

            if (!parsedOutput.Success)
            {
                return new OpenAIProviderResult(true, analysisJson, parsedOutput.Summary, parsedOutput.Score, parsedOutput.Recommendations, null);
            }

            return new OpenAIProviderResult(true, analysisJson, parsedOutput.Summary, parsedOutput.Score, parsedOutput.Recommendations, null);
        }

        private string GetRequestUri()
        {
            if (string.Equals(_settings.Provider, "AzureOpenAI", StringComparison.OrdinalIgnoreCase))
            {
                if (string.IsNullOrWhiteSpace(_settings.Endpoint))
                {
                    throw new InvalidOperationException("AISettings.Endpoint must be provided when Provider is AzureOpenAI.");
                }

                var endpoint = _settings.Endpoint.TrimEnd('/');
                var version = string.IsNullOrWhiteSpace(_settings.ApiVersion) ? "2024-12-01" : _settings.ApiVersion;
                return $"{endpoint}/openai/deployments/{_settings.Model}/chat/completions?api-version={version}";
            }

            return _settings.Endpoint?.TrimEnd('/') + "/v1/chat/completions" ?? "https://api.openai.com/v1/chat/completions";
        }

        private (bool Success, string RawOutput, string Summary, double Score, string Recommendations) ExtractContent(string rawJson)
        {
            try
            {
                using var document = JsonDocument.Parse(rawJson);
                var root = document.RootElement;
                var choice = root.TryGetProperty("choices", out var choices) && choices.GetArrayLength() > 0
                    ? choices[0]
                    : default;

                string rawOutput = string.Empty;
                if (choice.ValueKind != JsonValueKind.Undefined)
                {
                    if (choice.TryGetProperty("message", out var message) && message.TryGetProperty("content", out var content))
                    {
                        rawOutput = content.GetString() ?? string.Empty;
                    }
                    else if (choice.TryGetProperty("text", out var text))
                    {
                        rawOutput = text.GetString() ?? string.Empty;
                    }
                }

                if (string.IsNullOrWhiteSpace(rawOutput))
                {
                    return (true, rawOutput, string.Empty, 0, string.Empty);
                }

                var summary = string.Empty;
                var score = 0.0;
                var recommendations = string.Empty;

                try
                {
                    using var outputDoc = JsonDocument.Parse(rawOutput.Trim());
                    if (outputDoc.RootElement.TryGetProperty("summary", out var summaryToken))
                    {
                        summary = summaryToken.GetString() ?? string.Empty;
                    }
                    if (outputDoc.RootElement.TryGetProperty("score", out var scoreToken) && scoreToken.TryGetDouble(out var numericScore))
                    {
                        score = numericScore;
                    }
                    if (outputDoc.RootElement.TryGetProperty("recommendations", out var recommendationsToken))
                    {
                        recommendations = recommendationsToken.GetString() ?? string.Empty;
                    }
                }
                catch
                {
                    summary = rawOutput.Length <= 400 ? rawOutput : rawOutput[..400] + "...";
                    recommendations = "Review the analysis output for structured recommendations.";
                }

                return (true, rawOutput, summary, score, recommendations);
            }
            catch
            {
                return (false, string.Empty, string.Empty, 0, string.Empty);
            }
        }

        private sealed class OpenAIProviderResult : IAIProviderResult
        {
            public OpenAIProviderResult(bool success, string analysisJson, string summary, double score, string recommendations, string? message)
            {
                Success = success;
                AnalysisJson = analysisJson;
                Summary = summary;
                Score = score;
                Recommendations = recommendations;
                Message = message;
            }

            public bool Success { get; }
            public string AnalysisJson { get; }
            public string Summary { get; }
            public double Score { get; }
            public string Recommendations { get; }
            public string? Message { get; }
        }
    }
}
