// SPDX-License-Identifier: GPL-2.0-or-later
#ifndef VLC_REDESIGN_FOLDER_MODEL_HPP
#define VLC_REDESIGN_FOLDER_MODEL_HPP

#include <QAbstractListModel>
#include <QDir>
#include <QFileSystemWatcher>
#include <QUrl>
#include <QVariant>

// Qt Labs is deliberately excluded from VLC's static Qt contribs. Use native
// QDir + filesystem notifications instead, preserving the redesign's roles/API.
class RedesignFolderModel : public QAbstractListModel
{
    Q_OBJECT
    Q_PROPERTY(QUrl folder READ folder WRITE setFolder NOTIFY folderChanged)
    Q_PROPERTY(QStringList nameFilters READ nameFilters WRITE setNameFilters NOTIFY nameFiltersChanged)
    Q_PROPERTY(bool sortReversed READ sortReversed WRITE setSortReversed NOTIFY sortReversedChanged)
    Q_PROPERTY(int count READ count NOTIFY countChanged)
public:
    enum Role { FileName = Qt::UserRole + 1, FileUrl, FileIsDir };
    explicit RedesignFolderModel(QObject* parent = nullptr) : QAbstractListModel(parent)
    {
        connect(&m_watcher, &QFileSystemWatcher::directoryChanged, this, [this] { reload(); });
    }
    QUrl folder() const { return m_folder; }
    QStringList nameFilters() const { return m_filters; }
    bool sortReversed() const { return m_reversed; }
    int count() const { return m_entries.size(); }
    int rowCount(const QModelIndex& parent = QModelIndex()) const override
    { return parent.isValid() ? 0 : count(); }
    QHash<int, QByteArray> roleNames() const override
    { return {{FileName, "fileName"}, {FileUrl, "fileUrl"}, {FileIsDir, "fileIsDir"}}; }
    QVariant data(const QModelIndex& index, int role) const override
    {
        if (!index.isValid() || index.row() < 0 || index.row() >= count()) return {};
        const auto& entry = m_entries.at(index.row());
        switch (role) {
        case FileName: return entry.fileName();
        case FileUrl: return QUrl::fromLocalFile(entry.absoluteFilePath());
        case FileIsDir: return entry.isDir();
        default: return {};
        }
    }
    Q_INVOKABLE QVariant get(int row, const QString& property) const
    {
        const auto roles = roleNames();
        for (auto it = roles.cbegin(); it != roles.cend(); ++it)
            if (it.value() == property.toUtf8()) return data(index(row, 0), it.key());
        return {};
    }
    void setFolder(const QUrl& folder)
    {
        if (m_folder == folder) return;
        m_folder = folder;
        if (!m_watcher.directories().isEmpty()) m_watcher.removePaths(m_watcher.directories());
        if (folder.isLocalFile() && QDir(folder.toLocalFile()).exists())
            m_watcher.addPath(folder.toLocalFile());
        reload(); emit folderChanged();
    }
    void setNameFilters(const QStringList& filters)
    { if (m_filters == filters) return; m_filters = filters; reload(); emit nameFiltersChanged(); }
    void setSortReversed(bool reversed)
    { if (m_reversed == reversed) return; m_reversed = reversed; reload(); emit sortReversedChanged(); }
signals:
    void folderChanged();
    void nameFiltersChanged();
    void sortReversedChanged();
    void countChanged();
private:
    void reload()
    {
        beginResetModel();
        m_entries.clear();
        if (m_folder.isLocalFile()) {
            QDir dir(m_folder.toLocalFile());
            auto order = QDir::Name | QDir::DirsFirst | QDir::IgnoreCase;
            if (m_reversed) order |= QDir::Reversed;
            m_entries = dir.entryInfoList(m_filters,
                QDir::AllDirs | QDir::Files | QDir::NoDotAndDotDot | QDir::Readable, order);
        }
        endResetModel(); emit countChanged();
    }
    QUrl m_folder;
    QStringList m_filters;
    bool m_reversed = false;
    QFileInfoList m_entries;
    QFileSystemWatcher m_watcher;
};
#endif
