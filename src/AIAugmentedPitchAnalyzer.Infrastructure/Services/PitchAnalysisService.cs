using AIAugmentedPitchAnalyzer.Application.DTOs.Pitch;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IUnitOfWork;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using AutoMapper;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Infrastructure.Services
{
    public class PitchAnalysisService : IPitchAnalysisService
    {
        private readonly IPitchRepository _pitchRepository;
        private readonly IGenericRepository<PitchAnalysis> _analysisRepository;
        private readonly IUnitOfWork _unitOfWork;
        private readonly IPromptBuilder _promptBuilder;
        private readonly IAIProvider _aiProvider;
        private readonly IMapper _mapper;

        public PitchAnalysisService(
            IPitchRepository pitchRepository,
            IGenericRepository<PitchAnalysis> analysisRepository,
            IUnitOfWork unitOfWork,
            IPromptBuilder promptBuilder,
            IAIProvider aiProvider,
            IMapper mapper)
        {
            _pitchRepository = pitchRepository;
            _analysisRepository = analysisRepository;
            _unitOfWork = unitOfWork;
            _promptBuilder = promptBuilder;
            _aiProvider = aiProvider;
            _mapper = mapper;
        }

        public async Task<ApiResponse<PitchAnalysisResultDto>> AnalyzePitchAsync(Guid pitchId, Guid requestedBy)
        {
            var pitch = await _pitchRepository.GetByIdWithAnalysisAsync(pitchId);
            if (pitch == null)
            {
                return new ApiResponse<PitchAnalysisResultDto> { Success = false, Message = "Pitch not found." };
            }

            if (string.IsNullOrWhiteSpace(pitch.ExtractedText))
            {
                return new ApiResponse<PitchAnalysisResultDto> { Success = false, Message = "Pitch text must be extracted before analysis." };
            }

            var prompt = _promptBuilder.BuildPitchAnalysisPrompt(pitch);
            var aiResult = await _aiProvider.AnalyzeAsync(prompt);
            if (!aiResult.Success)
            {
                return new ApiResponse<PitchAnalysisResultDto> { Success = false, Message = aiResult.Message ?? "AI analysis failed." };
            }

            var analysis = pitch.Analysis ?? new PitchAnalysis
            {
                Id = Guid.NewGuid(),
                PitchId = pitch.Id
            };

            analysis.AnalysisJson = aiResult.AnalysisJson;
            analysis.Summary = aiResult.Summary;
            analysis.Score = aiResult.Score;
            analysis.Recommendations = aiResult.Recommendations;
            analysis.CompletedAt = DateTime.UtcNow;

            if (pitch.Analysis == null)
            {
                await _analysisRepository.AddAsync(analysis);
            }
            else
            {
                _analysisRepository.Update(analysis);
            }

            await _unitOfWork.SaveChangesAsync();

            return new ApiResponse<PitchAnalysisResultDto> { Data = _mapper.Map<PitchAnalysisResultDto>(analysis) };
        }

        public async Task<ApiResponse<PitchAnalysisDto>> GetPitchAnalysisAsync(Guid pitchId)
        {
            var pitch = await _pitchRepository.GetByIdWithAnalysisAsync(pitchId);
            if (pitch == null)
            {
                return new ApiResponse<PitchAnalysisDto> { Success = false, Message = "Pitch not found." };
            }

            if (pitch.Analysis == null)
            {
                return new ApiResponse<PitchAnalysisDto> { Success = false, Message = "No analysis exists for this pitch." };
            }

            return new ApiResponse<PitchAnalysisDto> { Data = _mapper.Map<PitchAnalysisDto>(pitch.Analysis) };
        }

        public async Task<ApiResponse<PitchAnalysisParsedDto>> GetParsedPitchAnalysisAsync(Guid pitchId)
        {
            var pitch = await _pitchRepository.GetByIdWithAnalysisAsync(pitchId);
            if (pitch == null)
            {
                return new ApiResponse<PitchAnalysisParsedDto> { Success = false, Message = "Pitch not found." };
            }

            if (pitch.Analysis == null)
            {
                return new ApiResponse<PitchAnalysisParsedDto> { Success = false, Message = "No analysis exists for this pitch." };
            }

            return new ApiResponse<PitchAnalysisParsedDto> { Data = _mapper.Map<PitchAnalysisParsedDto>(pitch.Analysis) };
        }

        public async Task<ApiResponse<PitchAnalysisDashboardDto>> GetDashboardAsync()
        {
            var pitches = await _pitchRepository.GetAllWithAnalysisAsync();
            var totalPitches = 0;
            var analyzedPitches = 0;
            var scores = new List<double>();

            foreach (var pitch in pitches)
            {
                totalPitches++;
                if (pitch.Analysis?.Score.HasValue == true)
                {
                    analyzedPitches++;
                    scores.Add(pitch.Analysis.Score.Value);
                }
            }

            var dashboard = new PitchAnalysisDashboardDto
            {
                TotalPitches = totalPitches,
                AnalyzedPitches = analyzedPitches,
                PendingAnalysis = totalPitches - analyzedPitches,
                AverageScore = scores.Count > 0 ? Math.Round(scores.Average(), 2) : 0,
                HighestScore = scores.Count > 0 ? scores.Max() : 0,
                LowestScore = scores.Count > 0 ? scores.Min() : 0
            };

            return new ApiResponse<PitchAnalysisDashboardDto> { Data = dashboard };
        }

        public async Task<ApiResponse<IEnumerable<PitchAnalysisHistoryDto>>> GetAnalysisHistoryAsync()
        {
            var pitches = await _pitchRepository.GetAllWithAnalysisAsync();
            var history = pitches
                .Where(p => p.Analysis != null)
                .Select(p => new PitchAnalysisHistoryDto
                {
                    PitchId = p.Id,
                    PitchTitle = p.Title,
                    AnalysisId = p.Analysis!.Id,
                    Summary = p.Analysis.Summary ?? string.Empty,
                    Score = p.Analysis.Score,
                    Recommendations = p.Analysis.Recommendations,
                    CompletedAt = p.Analysis.CompletedAt
                })
                .OrderByDescending(item => item.CompletedAt)
                .ToList();

            return new ApiResponse<IEnumerable<PitchAnalysisHistoryDto>> { Data = history };
        }
    }
}
