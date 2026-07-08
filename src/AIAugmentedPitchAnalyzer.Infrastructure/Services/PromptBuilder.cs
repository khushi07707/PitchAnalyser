using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using System.Text;

namespace AIAugmentedPitchAnalyzer.Infrastructure.Services
{
    public class PromptBuilder : IPromptBuilder
    {
        public string BuildPitchAnalysisPrompt(Pitch pitch)
        {
            var prompt = new StringBuilder();
            prompt.AppendLine("You are an AI analyst for startup pitch decks.");
            prompt.AppendLine("Review the pitch content and return a concise analysis in JSON format.");
            prompt.AppendLine("Include the following:");
            prompt.AppendLine("- summary");
            prompt.AppendLine("- normalized score from 0 to 100");
            prompt.AppendLine("- practical recommendations for improvement");
            prompt.AppendLine();
            prompt.AppendLine("Pitch title:");
            prompt.AppendLine(pitch.Title);
            prompt.AppendLine();
            prompt.AppendLine("Pitch text:");
            prompt.AppendLine(pitch.ExtractedText ?? "[No extracted pitch content available]");
            prompt.AppendLine();
            prompt.AppendLine("Answer in JSON with keys: summary, score, recommendations, details.");
            prompt.AppendLine("Do not include additional explanation outside the JSON object.");
            return prompt.ToString();
        }
    }
}
