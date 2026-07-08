using AIAugmentedPitchAnalyzer.Domain.Entities;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface IPromptBuilder
    {
        string BuildPitchAnalysisPrompt(Pitch pitch);
    }
}
