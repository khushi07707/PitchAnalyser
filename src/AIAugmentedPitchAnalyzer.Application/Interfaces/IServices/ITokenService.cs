using AIAugmentedPitchAnalyzer.Domain.Entities;
using System;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface ITokenService
    {
        string GenerateToken(User user);
    }
}
