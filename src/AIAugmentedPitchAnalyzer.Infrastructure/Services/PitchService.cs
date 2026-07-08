using AIAugmentedPitchAnalyzer.Application.DTOs.Pitch;
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
    public class PitchService : IPitchService
    {
        private readonly IPitchRepository _pitchRepository;
        private readonly IUnitOfWork _unitOfWork;
        private readonly IMapper _mapper;
        private readonly IFileService _fileService;

        public PitchService(IPitchRepository pitchRepository, IUnitOfWork unitOfWork, IMapper mapper, IFileService fileService)
        {
            _pitchRepository = pitchRepository;
            _unitOfWork = unitOfWork;
            _mapper = mapper;
            _fileService = fileService;
        }

        public async Task<ApiResponse<PitchDto>> UploadPitchAsync(UploadPitchRequest request, Guid uploadedBy)
        {
            var pitch = _mapper.Map<Pitch>(request);
            await _pitchRepository.AddAsync(pitch);
            await _unitOfWork.SaveChangesAsync();
            var dto = _mapper.Map<PitchDto>(pitch);
            return new ApiResponse<PitchDto> { Data = dto };
        }

        public async Task<ApiResponse<PitchDto>> UploadPitchWithFileAsync(UploadPitchRequest request, System.IO.Stream fileStream, string fileName, string contentType, long size, Guid uploadedBy, string storagePath)
        {
            var uploadResult = await _fileService.UploadFileAsync(fileStream, fileName, contentType, size, uploadedBy, storagePath);
            if (!uploadResult.Success || uploadResult.Data == null)
            {
                return new ApiResponse<PitchDto> { Success = false, Message = uploadResult.Message ?? "File upload failed." };
            }

            var extractedResult = await _fileService.ExtractTextAsync(uploadResult.Data.Id);

            var pitch = _mapper.Map<Pitch>(request);
            pitch.FileRecordId = uploadResult.Data.Id;
            pitch.ExtractedText = extractedResult.Success ? extractedResult.Data : null;

            await _pitchRepository.AddAsync(pitch);
            await _unitOfWork.SaveChangesAsync();

            var dto = _mapper.Map<PitchDto>(pitch);
            return new ApiResponse<PitchDto> { Data = dto };
        }

        public async Task<ApiResponse<PitchDto>> GetPitchAsync(Guid id)
        {
            var p = await _pitchRepository.GetByIdWithAnalysisAsync(id);
            if (p == null) return new ApiResponse<PitchDto> { Success = false, Message = "Pitch not found" };
            var dto = _mapper.Map<PitchDto>(p);
            return new ApiResponse<PitchDto> { Data = dto };
        }

        public async Task<ApiResponse<IEnumerable<PitchDto>>> GetAllPitchesAsync()
        {
            var pitches = await _pitchRepository.GetAllWithAnalysisAsync();
            var dtos = _mapper.Map<IEnumerable<PitchDto>>(pitches);
            return new ApiResponse<IEnumerable<PitchDto>> { Data = dtos };
        }

        public async Task<ApiResponse<IEnumerable<PitchDto>>> GetPitchesByStartupAsync(Guid startupId)
        {
            var pitches = await _pitchRepository.GetByStartupIdAsync(startupId);
            var dtos = _mapper.Map<IEnumerable<PitchDto>>(pitches);
            return new ApiResponse<IEnumerable<PitchDto>> { Data = dtos };
        }
    }
}
