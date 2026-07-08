using AIAugmentedPitchAnalyzer.Application.DTOs.Startup;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using System;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface IStartupService
    {
        Task<ApiResponse<StartupDto>> CreateStartupAsync(CreateStartupRequest request, Guid createdBy);
        Task<ApiResponse<StartupDto>> GetStartupAsync(Guid id);
        Task<ApiResponse<AIAugmentedPitchAnalyzer.Shared.Responses.PagedResult<StartupDto>>> GetAllAsync(int pageNumber = 1, int pageSize = 20, AIAugmentedPitchAnalyzer.Domain.Enums.Industry? industry = null, string? search = null);
        Task<ApiResponse<StartupDto>> UpdateStartupAsync(Guid id, UpdateStartupRequest request, Guid updatedBy);
        Task<ApiResponse<bool>> DeleteStartupAsync(Guid id, Guid deletedBy);
    }
}
