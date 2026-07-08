using AIAugmentedPitchAnalyzer.Shared.Responses;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface ITextExtractionService
    {
        Task<ApiResponse<string>> ExtractTextFromFileAsync(string filePath, string? contentType = null);
    }
}
