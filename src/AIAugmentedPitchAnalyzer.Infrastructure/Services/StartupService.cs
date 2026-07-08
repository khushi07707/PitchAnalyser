using AIAugmentedPitchAnalyzer.Application.DTOs.Startup;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IUnitOfWork;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using AutoMapper;
using System;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Infrastructure.Services
{
    public class StartupService : IStartupService
    {
        private readonly IStartupRepository _startupRepository;
        private readonly IUnitOfWork _unitOfWork;
        private readonly IMapper _mapper;

        public StartupService(IStartupRepository startupRepository, IUnitOfWork unitOfWork, IMapper mapper)
        {
            _startupRepository = startupRepository;
            _unitOfWork = unitOfWork;
            _mapper = mapper;
        }

        public async Task<ApiResponse<StartupDto>> CreateStartupAsync(CreateStartupRequest request, Guid createdBy)
        {
            var startup = _mapper.Map<Startup>(request);
            startup.CreatedById = createdBy;
            await _startupRepository.AddAsync(startup);
            await _unitOfWork.SaveChangesAsync();

            var dto = _mapper.Map<StartupDto>(startup);
            return new ApiResponse<StartupDto> { Data = dto };
        }

        public async Task<ApiResponse<StartupDto>> GetStartupAsync(Guid id)
        {
            var entity = await _startupRepository.GetWithPitchesAsync(id);
            if (entity == null) return new ApiResponse<StartupDto> { Success = false, Message = "Startup not found" };
            var dto = _mapper.Map<StartupDto>(entity);
            return new ApiResponse<StartupDto> { Data = dto };
        }

        public async Task<ApiResponse<Shared.Responses.PagedResult<StartupDto>>> GetAllAsync(int pageNumber = 1, int pageSize = 20, Domain.Enums.Industry? industry = null, string? search = null)
        {
            var (items, total) = await _startupRepository.GetPagedAsync(pageNumber, pageSize, industry, search);

            var dtos = _mapper.Map<IEnumerable<StartupDto>>(items);

            var paged = new Shared.Responses.PagedResult<StartupDto>
            {
                Items = dtos,
                TotalCount = total,
                PageNumber = Math.Max(1, pageNumber),
                PageSize = Math.Max(1, pageSize)
            };

            paged.TotalPages = (int)Math.Ceiling((double)total / paged.PageSize);

            return new ApiResponse<Shared.Responses.PagedResult<StartupDto>> { Data = paged };
        }

        public async Task<ApiResponse<StartupDto>> UpdateStartupAsync(Guid id, Application.DTOs.Startup.UpdateStartupRequest request, Guid updatedBy)
        {
            var entity = await _startupRepository.GetByIdAsync(id);
            if (entity == null) return new ApiResponse<StartupDto> { Success = false, Message = "Startup not found" };

            // apply updates if provided
            if (!string.IsNullOrWhiteSpace(request.Name)) entity.Name = request.Name!;
            if (!string.IsNullOrWhiteSpace(request.FounderName)) entity.FounderName = request.FounderName!;
            if (!string.IsNullOrWhiteSpace(request.FounderEmail)) entity.FounderEmail = request.FounderEmail!;
            if (request.Industry.HasValue) entity.Industry = request.Industry.Value;
            if (request.FundingStage.HasValue) entity.FundingStage = (Domain.Enums.FundingStage)request.FundingStage.Value;
            if (!string.IsNullOrWhiteSpace(request.BusinessDescription)) entity.BusinessDescription = request.BusinessDescription!;
            if (!string.IsNullOrWhiteSpace(request.WebsiteUrl)) entity.WebsiteUrl = request.WebsiteUrl;

            _startupRepository.Update(entity);
            await _unitOfWork.SaveChangesAsync();

            var dto = _mapper.Map<StartupDto>(entity);
            return new ApiResponse<StartupDto> { Data = dto };
        }

        public async Task<ApiResponse<bool>> DeleteStartupAsync(Guid id, Guid deletedBy)
        {
            var entity = await _startupRepository.GetByIdAsync(id);
            if (entity == null) return new ApiResponse<bool> { Success = false, Message = "Startup not found", Data = false };

            _startupRepository.Remove(entity);
            await _unitOfWork.SaveChangesAsync();

            return new ApiResponse<bool> { Data = true };
        }
    }
}
