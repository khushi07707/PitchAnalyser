using AIAugmentedPitchAnalyzer.Domain.Entities;
using System;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository
{
    public interface IUserRepository : IGenericRepository<User>
    {
        Task<User?> GetByEmailAsync(string email);
    }
}
