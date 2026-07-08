using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface IAIProvider
    {
        Task<IAIProviderResult> AnalyzeAsync(string prompt);
    }
}
