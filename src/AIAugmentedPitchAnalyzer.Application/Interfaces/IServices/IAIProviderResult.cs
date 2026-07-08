namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface IAIProviderResult
    {
        bool Success { get; }
        string AnalysisJson { get; }
        string Summary { get; }
        double Score { get; }
        string Recommendations { get; }
        string? Message { get; }
    }
}
